#include "Combat/NRProjetilMagico.h"

#include "Components/PointLightComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/DamageType.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "UObject/ConstructorHelpers.h"

ANRProjetilMagico::ANRProjetilMagico()
{
	PrimaryActorTick.bCanEverTick = false;
	InitialLifeSpan = 3.f;

	// Bloqueia o cenário e sobrepõe pawns: assim atravessa gatilhos sem explodir e acerta creeps pela cápsula.
	Esfera = CreateDefaultSubobject<USphereComponent>(TEXT("Esfera"));
	Esfera->InitSphereRadius(15.f);
	Esfera->SetCollisionObjectType(ECC_WorldDynamic);
	Esfera->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Esfera->SetCollisionResponseToAllChannels(ECR_Block);
	Esfera->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	Esfera->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	Esfera->SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
	Esfera->SetGenerateOverlapEvents(true);
	Esfera->SetCanEverAffectNavigation(false);
	RootComponent = Esfera;

	Malha = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Malha"));
	Malha->SetupAttachment(Esfera);
	Malha->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Malha->SetCastShadow(false);
	// Custom depth com stencil 4 (magia): fica fora do filtro de aquarela e ganha contorno nítido (GDD §10).
	// Stencils: 1 herói, 2 creep, 3 pickup, 4 magia.
	Malha->SetRenderCustomDepth(true);
	Malha->SetCustomDepthStencilValue(4);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Esferinha(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (Esferinha.Succeeded())
	{
		Malha->SetStaticMesh(Esferinha.Object);
	}

	Luz = CreateDefaultSubobject<UPointLightComponent>(TEXT("Luz"));
	Luz->SetupAttachment(Esfera);
	Luz->SetIntensity(8000.f);
	Luz->SetAttenuationRadius(350.f);
	Luz->SetCastShadows(false);

	Movimento = CreateDefaultSubobject<UProjectileMovementComponent>(TEXT("Movimento"));
	Movimento->UpdatedComponent = Esfera;
	Movimento->ProjectileGravityScale = 0.f;
	Movimento->bRotationFollowsVelocity = true;
	Movimento->bShouldBounce = false;
}

void ANRProjetilMagico::BeginPlay()
{
	Super::BeginPlay();
	if (APawn* Quem = GetInstigator())
	{
		Esfera->IgnoreActorWhenMoving(Quem, true);
	}
	Esfera->OnComponentBeginOverlap.AddDynamic(this, &ThisClass::AoSobrepor);
	Movimento->OnProjectileStop.AddDynamic(this, &ThisClass::AoParar);
}

void ANRProjetilMagico::Lancar(const FVector& Direcao, float Velocidade, float Alcance, const FLinearColor& Cor, float Escala,
                               USceneComponent* Alvo, float Teleguiado)
{
	if (Alvo && Teleguiado > 0.f)
	{
		Movimento->bIsHomingProjectile = true;
		Movimento->HomingTargetComponent = Alvo;
		Movimento->HomingAccelerationMagnitude = Teleguiado;
	}
	CorAtual = Cor;
	Malha->SetRelativeScale3D(FVector(Escala));
	Esfera->SetSphereRadius(FMath::Max(10.f, 30.f * Escala));
	if (Material)
	{
		if (UMaterialInstanceDynamic* MID = Malha->CreateDynamicMaterialInstance(0, Material))
		{
			MID->SetVectorParameterValue(TEXT("Cor"), Cor);
		}
	}
	Luz->SetLightColor(Cor);
	Movimento->MaxSpeed = Velocidade;
	Movimento->Velocity = Direcao.GetSafeNormal() * Velocidade;
	SetLifeSpan(FMath::Max(0.1f, Alcance / FMath::Max(1.f, Velocidade)));

	// Lançado colado num inimigo (corpo a corpo): a sobreposição inicial acontece no spawn, antes do
	// BeginPlay ligar o evento, e não se repete. Então confere aqui.
	TArray<AActor*> Encostados;
	Esfera->GetOverlappingActors(Encostados, APawn::StaticClass());
	for (AActor* Ator : Encostados)
	{
		if (Ator && Ator != GetInstigator())
		{
			Explodir(Ator, GetActorLocation());
			return;
		}
	}
}

void ANRProjetilMagico::AoSobrepor(UPrimitiveComponent* Componente, AActor* Outro, UPrimitiveComponent* OutroComponente,
                                    int32 Indice, bool bVarredura, const FHitResult& Hit)
{
	// Só pawns (creeps e heróis); gatilhos de baú, pickups e afins não contam.
	if (!Outro || Outro == this || Outro == GetInstigator() || !Outro->IsA<APawn>())
	{
		return;
	}
	Explodir(Outro, GetActorLocation());
}

void ANRProjetilMagico::AoParar(const FHitResult& Hit)
{
	// Sai um pouco da superfície para o teste de linha de visão do dano em área não começar dentro do chão.
	const FVector Ponto = Hit.bBlockingHit ? FVector(Hit.ImpactPoint + Hit.ImpactNormal * 20.f) : GetActorLocation();
	Explodir(Hit.GetActor(), Ponto);
}

void ANRProjetilMagico::Explodir(AActor* Alvo, const FVector& Ponto)
{
	if (bExplodiu)
	{
		return;
	}
	bExplodiu = true;

	if (HasAuthority())
	{
		AController* Quem = GetInstigatorController();
		if (RaioExplosao > 0.f)
		{
			TArray<AActor*> Ignorar;
			if (GetInstigator())
			{
				Ignorar.Add(GetInstigator());
			}
			UGameplayStatics::ApplyRadialDamage(this, Dano, Ponto, RaioExplosao, UDamageType::StaticClass(), Ignorar, this, Quem, true);
		}
		else if (Alvo && Alvo != GetInstigator() && Alvo->IsA<APawn>())
		{
			UGameplayStatics::ApplyDamage(Alvo, Dano, Quem, this, UDamageType::StaticClass());
		}
	}

	// Clarão: a esfera cresce até o tamanho da explosão e some logo depois.
	Movimento->StopMovementImmediately();
	Esfera->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	SetActorLocation(Ponto);
	const float Diametro = FMath::Max(RaioExplosao * 2.f, 60.f);
	Malha->SetWorldScale3D(FVector(Diametro / 100.f));
	Luz->SetIntensity(Luz->Intensity * 4.f);
	Luz->SetAttenuationRadius(FMath::Max(Diametro * 2.f, 400.f));
	SetLifeSpan(0.15f);
}
