#include "Combat/NRChuvaMeteoros.h"

#include "Combat/NREstruturaMagica.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/OverlapResult.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/DamageType.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "NexusRoyale.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	/** Cada meteoro leva isso para cair, e começa a cair durante o aviso. */
	constexpr float TempoQueda = 0.6f;
	constexpr float AlturaQueda = 1800.f;
	/** Duração do clarão de cada explosão. */
	constexpr float TempoClarao = 0.15f;
	constexpr float IntervaloQueima = 0.5f;
	/** Diâmetro do meteoro em voo, em metros. */
	constexpr float DiametroMeteoro = 1.4f;
	/** Nos últimos segundos, o chão em chamas vai apagando. */
	constexpr float TempoApagar = 0.5f;
}

ANRChuvaMeteoros::ANRChuvaMeteoros()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = false;

	Raiz = CreateDefaultSubobject<USceneComponent>(TEXT("Raiz"));
	RootComponent = Raiz;

	// Stencils: 1 herói, 2 creep, 3 pickup, 4 magia (fora do filtro de aquarela, com contorno nítido; GDD §10).
	Disco = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Disco"));
	Disco->SetupAttachment(Raiz);
	Disco->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Disco->SetCastShadow(false);
	Disco->SetRenderCustomDepth(true);
	Disco->SetCustomDepthStencilValue(4);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cilindro(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (Cilindro.Succeeded())
	{
		Disco->SetStaticMesh(Cilindro.Object);
	}

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Esfera(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (Esfera.Succeeded())
	{
		MalhaMeteoro = Esfera.Object;
	}

	Luz = CreateDefaultSubobject<UPointLightComponent>(TEXT("Luz"));
	Luz->SetupAttachment(Raiz);
	Luz->SetRelativeLocation(FVector(0.f, 0.f, 150.f));
	Luz->SetIntensity(0.f);
	Luz->SetCastShadows(false);
}

void ANRChuvaMeteoros::Iniciar(const FNRMagiaChuva& Config, float MultiplicadorDano, UMaterialInterface* Material)
{
	Cfg = Config;
	Cfg.Meteoros = FMath::Max(1, Cfg.Meteoros);
	Multiplicador = FMath::Max(0.f, MultiplicadorDano);
	const float R = FMath::Max(50.f, Cfg.RaioArea);

	// O cilindro da engine tem 1 m de diâmetro e de altura: vira um disco de 3 cm do tamanho da área.
	Disco->SetRelativeScale3D(FVector(2.f * R / 100.f, 2.f * R / 100.f, 0.03f));
	Disco->SetRelativeLocation(FVector(0.f, 0.f, 3.f));
	if (Material)
	{
		MIDDisco = Disco->CreateDynamicMaterialInstance(0, Material);
	}
	Luz->SetLightColor(Cfg.Cor);
	Luz->SetAttenuationRadius(R * 2.5f);

	// Meteoros a meio raio do centro, em ângulos iguais (um só cai no centro), vindo todos da mesma diagonal.
	const FVector Centro = GetActorLocation();
	const FRotator Plano = GetActorRotation(); // o disco segue a inclinação do chão
	const float Giro = FMath::FRandRange(0.f, 360.f);
	const FVector De = FRotator(0.f, FMath::FRandRange(0.f, 360.f), 0.f).Vector();
	for (int32 i = 0; i < Cfg.Meteoros; ++i)
	{
		FVector Ponto = Centro;
		if (Cfg.Meteoros > 1)
		{
			Ponto += Plano.RotateVector(FRotator(0.f, Giro + 360.f * i / Cfg.Meteoros, 0.f).Vector() * R * 0.5f);
		}
		Impactos.Add(Ponto);
		Partidas.Add(Ponto + De * AlturaQueda * 0.45f + FVector(0.f, 0.f, AlturaQueda));

		// Sem anexar: a posição é sempre a do mundo.
		UStaticMeshComponent* Meteoro = NewObject<UStaticMeshComponent>(this);
		Meteoro->SetStaticMesh(MalhaMeteoro);
		Meteoro->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Meteoro->SetCastShadow(false);
		Meteoro->SetRenderCustomDepth(true);
		Meteoro->SetCustomDepthStencilValue(4);
		Meteoro->RegisterComponent();
		Meteoro->SetWorldLocationAndRotation(Partidas.Last(), FRotator::ZeroRotator);
		Meteoro->SetWorldScale3D(FVector(DiametroMeteoro));
		Meteoro->SetVisibility(false);
		if (Material)
		{
			if (UMaterialInstanceDynamic* MID = Meteoro->CreateDynamicMaterialInstance(0, Material))
			{
				MID->SetVectorParameterValue(TEXT("Cor"), Cfg.Cor);
			}
		}
		Meteoros.Add(Meteoro);
	}

	bIniciada = true;
	SetActorTickEnabled(true);
}

float ANRChuvaMeteoros::InstanteImpacto(int32 Indice) const
{
	return FMath::Max(0.f, Cfg.Aviso) + Indice * FMath::Max(0.f, Cfg.IntervaloMeteoros);
}

void ANRChuvaMeteoros::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	if (!bIniciada)
	{
		return;
	}
	Tempo += DeltaTime;

	// Impactos que já chegaram na hora.
	while (ProximoImpacto < Meteoros.Num() && Tempo >= InstanteImpacto(ProximoImpacto))
	{
		Impacto(ProximoImpacto++);
	}

	// Meteoros caindo (acelerando) e clarões que já acabaram.
	for (int32 i = 0; i < Meteoros.Num(); ++i)
	{
		UStaticMeshComponent* Meteoro = Meteoros[i];
		const float Cai = InstanteImpacto(i);
		if (i < ProximoImpacto)
		{
			if (Tempo >= Cai + TempoClarao)
			{
				Meteoro->SetVisibility(false);
			}
		}
		else if (Tempo >= Cai - TempoQueda)
		{
			const float A = FMath::Clamp(1.f - (Cai - Tempo) / TempoQueda, 0.f, 1.f);
			Meteoro->SetVisibility(true);
			Meteoro->SetWorldLocation(FMath::Lerp(Partidas[i], Impactos[i], A * A));
		}
	}

	// Disco: aviso piscando até o primeiro impacto, depois chão em chamas.
	const float FimChamas = InstanteImpacto(0) + FMath::Max(0.f, Cfg.DuracaoChamas);
	FLinearColor CorDisco;
	if (ProximoImpacto == 0)
	{
		CorDisco = Cfg.Cor * (0.12f + 0.08f * FMath::Sin(Tempo * 20.f));
	}
	else if (Tempo < FimChamas)
	{
		const float Tremor = FMath::FRandRange(0.8f, 1.2f);
		const float Apaga = FMath::Clamp((FimChamas - Tempo) / TempoApagar, 0.f, 1.f);
		CorDisco = Cfg.Cor * (0.45f * Tremor * Apaga);
		Luz->SetIntensity(15000.f * Tremor * Apaga);
		while (Tempo >= ProximaQueima && ProximaQueima < FimChamas)
		{
			QueimarChao();
			ProximaQueima += IntervaloQueima;
		}
	}
	else
	{
		CorDisco = FLinearColor::Black;
		Disco->SetVisibility(false);
		Luz->SetIntensity(0.f);
		if (Tempo >= InstanteImpacto(Meteoros.Num() - 1) + TempoClarao)
		{
			Destroy();
			return;
		}
	}
	if (MIDDisco)
	{
		CorDisco.A = 1.f;
		MIDDisco->SetVectorParameterValue(TEXT("Cor"), CorDisco);
	}
}

void ANRChuvaMeteoros::Impacto(int32 Indice)
{
	const FVector Ponto = Impactos[Indice];
	UStaticMeshComponent* Meteoro = Meteoros[Indice];
	// Clarão do tamanho da explosão.
	Meteoro->SetVisibility(true);
	Meteoro->SetWorldLocation(Ponto);
	Meteoro->SetWorldScale3D(FVector(FMath::Max(Cfg.RaioMeteoro * 2.f, 60.f) / 100.f));
	if (Indice == 0)
	{
		ProximaQueima = Tempo; // o chão começa a queimar no primeiro impacto
	}
	if (!HasAuthority())
	{
		return;
	}

	TArray<FOverlapResult> Sobrepostos;
	FCollisionObjectQueryParams Tipos;
	Tipos.AddObjectTypesToQuery(ECC_Pawn);
	Tipos.AddObjectTypesToQuery(ECC_WorldDynamic);
	const FCollisionQueryParams Params(SCENE_QUERY_STAT(NRMeteoro), false, GetInstigator());
	GetWorld()->OverlapMultiByObjectType(Sobrepostos, Ponto + FVector(0.f, 0.f, 50.f), FQuat::Identity, Tipos,
		FCollisionShape::MakeSphere(Cfg.RaioMeteoro), Params);

	AController* Quem = GetInstigatorController();
	int32 Novos = 0;
	for (const FOverlapResult& Sobreposto : Sobrepostos)
	{
		AActor* Alvo = Sobreposto.GetActor();
		if (!Alvo || Alvo == GetInstigator() || Atingidos.Contains(Alvo))
		{
			continue;
		}
		if (!Alvo->IsA<APawn>() && !Alvo->IsA<ANREstruturaMagica>())
		{
			continue;
		}
		Atingidos.Add(Alvo);
		++Novos;
		UGameplayStatics::ApplyDamage(Alvo, Cfg.DanoMeteoro * Multiplicador, Quem, this, UDamageType::StaticClass());
	}
	UE_LOG(LogNexus, Log, TEXT("%s: meteoro %d acertou %d alvo(s)"), *GetName(), Indice + 1, Novos);
}

void ANRChuvaMeteoros::QueimarChao()
{
	if (!HasAuthority() || Cfg.DanoChamasPorSegundo <= 0.f)
	{
		return;
	}
	const float R = FMath::Max(50.f, Cfg.RaioArea);
	const FVector Centro = GetActorLocation();
	TArray<FOverlapResult> Sobrepostos;
	const FCollisionQueryParams Params(SCENE_QUERY_STAT(NRChamas), false, GetInstigator());
	GetWorld()->OverlapMultiByObjectType(Sobrepostos, Centro + FVector(0.f, 0.f, 100.f), FQuat::Identity,
		FCollisionObjectQueryParams(ECC_Pawn), FCollisionShape::MakeBox(FVector(R, R, 200.f)), Params);

	AController* Quem = GetInstigatorController();
	const float Dano = Cfg.DanoChamasPorSegundo * IntervaloQueima * Multiplicador;
	TSet<const AActor*> Queimados;
	for (const FOverlapResult& Sobreposto : Sobrepostos)
	{
		AActor* Alvo = Sobreposto.GetActor();
		if (!Alvo || Alvo == GetInstigator() || !Alvo->IsA<APawn>() || Queimados.Contains(Alvo))
		{
			continue;
		}
		if (FVector::Dist2D(Alvo->GetActorLocation(), Centro) > R)
		{
			continue; // a caixa da consulta é quadrada; a área é redonda
		}
		Queimados.Add(Alvo);
		UGameplayStatics::ApplyDamage(Alvo, Dano, Quem, this, UDamageType::StaticClass());
	}
}
