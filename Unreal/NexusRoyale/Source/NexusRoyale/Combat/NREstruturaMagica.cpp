#include "Combat/NREstruturaMagica.h"

#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/CollisionProfile.h"
#include "Engine/DamageEvents.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "NexusRoyale.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	constexpr float TempoSubir = 0.15f;
	constexpr float TempoAfundar = 0.3f;
	/** Quanto a base entra no chão, para não ficar no ar nos declives. */
	constexpr float Afundar = 20.f;
}

ANREstruturaMagica::ANREstruturaMagica()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = true;

	// Bloqueia pawns, projéteis e o teste de linha de visão do dano em área (Visibility). A câmera atravessa,
	// para não pular para perto do herói quando a muralha fica entre os dois.
	Caixa = CreateDefaultSubobject<UBoxComponent>(TEXT("Caixa"));
	Caixa->InitBoxExtent(FVector(30.f, 300.f, 175.f));
	Caixa->SetCollisionProfileName(UCollisionProfile::BlockAllDynamic_ProfileName);
	Caixa->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	Caixa->SetCanEverAffectNavigation(false);
	RootComponent = Caixa;

	Malha = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Malha"));
	Malha->SetupAttachment(Caixa);
	Malha->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	// Stencils: 1 herói, 2 creep, 3 pickup, 4 magia (fora do filtro de aquarela, com contorno nítido; GDD §10).
	Malha->SetRenderCustomDepth(true);
	Malha->SetCustomDepthStencilValue(4);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cubo(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (Cubo.Succeeded())
	{
		Malha->SetStaticMesh(Cubo.Object);
	}
}

void ANREstruturaMagica::Erguer(const FVector& Tamanho, float NovaVida, float Duracao, const FLinearColor& Cor, UMaterialInterface* Material)
{
	const FVector T = Tamanho.ComponentMax(FVector(10.f));
	Altura = T.Z;
	VidaMax = Vida = FMath::Max(1.f, NovaVida);
	CorBase = Cor;

	SetActorLocation(GetActorLocation() + FVector(0.f, 0.f, T.Z * 0.5f - Afundar));
	Caixa->SetBoxExtent(T * 0.5f);
	Malha->SetRelativeScale3D(T / 100.f); // o cubo da engine tem 1 m de lado
	Malha->SetRelativeLocation(FVector(0.f, 0.f, -Altura)); // começa enterrada e sobe no Tick
	if (Material)
	{
		MID = Malha->CreateDynamicMaterialInstance(0, Material);
	}
	AtualizarCor();

	TempoAnim = 0.f;
	if (Duracao > 0.f)
	{
		GetWorldTimerManager().SetTimer(TimerDuracao, this, &ThisClass::Desfazer, Duracao, false);
	}
	SetActorTickEnabled(true);
}

void ANREstruturaMagica::Desfazer()
{
	if (bDesfazendo)
	{
		return;
	}
	bDesfazendo = true;
	GetWorldTimerManager().ClearTimer(TimerDuracao);
	Caixa->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	// Se ainda estava subindo, afunda a partir da altura em que parou.
	const float Enterrada = Altura > 0.f ? FMath::Clamp(-Malha->GetRelativeLocation().Z / Altura, 0.f, 1.f) : 0.f;
	TempoAnim = Enterrada * TempoAfundar;
	SetActorTickEnabled(true);
	UE_LOG(LogNexus, Log, TEXT("%s se desfez (vida %.0f/%.0f)"), *GetName(), Vida, VidaMax);
}

float ANREstruturaMagica::TempoRestante() const
{
	return bDesfazendo ? 0.f : FMath::Max(0.f, GetWorldTimerManager().GetTimerRemaining(TimerDuracao));
}

float ANREstruturaMagica::TakeDamage(float Dano, FDamageEvent const& Evento, AController* Instigador, AActor* Causador)
{
	if (bDesfazendo || Dano <= 0.f)
	{
		return 0.f;
	}
	if (Instigador && Instigador == GetInstigatorController())
	{
		return 0.f; // tiro do próprio dono: bloqueia, mas não estraga
	}
	const float Real = Super::TakeDamage(Dano, Evento, Instigador, Causador);
	if (Real <= 0.f)
	{
		return 0.f;
	}
	Vida = FMath::Max(0.f, Vida - Real);
	AtualizarCor();
	if (Vida <= 0.f)
	{
		Desfazer();
	}
	return Real;
}

void ANREstruturaMagica::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	TempoAnim += DeltaTime;
	if (bDesfazendo)
	{
		const float A = FMath::Clamp(TempoAnim / TempoAfundar, 0.f, 1.f);
		Malha->SetRelativeLocation(FVector(0.f, 0.f, -Altura * A));
		if (A >= 1.f)
		{
			Destroy();
		}
		return;
	}
	const float A = FMath::Clamp(TempoAnim / TempoSubir, 0.f, 1.f);
	Malha->SetRelativeLocation(FVector(0.f, 0.f, -Altura * (1.f - A)));
	if (A >= 1.f)
	{
		SetActorTickEnabled(false);
	}
}

void ANREstruturaMagica::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	GetWorldTimerManager().ClearTimer(TimerDuracao);
	Super::EndPlay(EndPlayReason);
}

void ANREstruturaMagica::AtualizarCor()
{
	if (MID)
	{
		// Escurece conforme perde vida: dá para ver de longe que a muralha está quase caindo.
		const float Fracao = VidaMax > 0.f ? Vida / VidaMax : 0.f;
		FLinearColor Cor = CorBase * (0.35f + 0.65f * Fracao);
		Cor.A = 1.f;
		MID->SetVectorParameterValue(TEXT("Cor"), Cor);
	}
}
