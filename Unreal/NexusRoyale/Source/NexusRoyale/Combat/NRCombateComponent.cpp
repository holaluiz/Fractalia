#include "Combat/NRCombateComponent.h"

#include "Combat/NRProjetilMagico.h"
#include "Components/SkeletalMeshComponent.h"
#include "EngineUtils.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GAS/AS_Hero.h"
#include "GAS/NRAbilitySystemComponent.h"
#include "InputAction.h"
#include "Items/NRInventoryComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NexusRoyale.h"
#include "TimerManager.h"
#include "UI/NRHudWidget.h"

UNRCombateComponent::UNRCombateComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickInterval = 0.1f;

	// Feiticeiro (GDD §4.1): dardo arcano, 60 mágico, 35 m, 1 a cada 1,0 s.
	AtaqueBasico.Nome = NSLOCTEXT("Nexus", "DardoArcano", "Dardo arcano");
	AtaqueBasico.Dano = 60.f;
	AtaqueBasico.Alcance = 3500.f;
	AtaqueBasico.Velocidade = 4500.f;
	AtaqueBasico.Recarga = 1.f;
	AtaqueBasico.Cor = FLinearColor(0.55f, 0.35f, 1.f);
	AtaqueBasico.Tamanho = 0.25f;
	AtaqueBasico.Teleguiado = 12000.f; // "levemente teleguiado": raio de curva de ~17 m a 45 m/s

	// Bola de Fogo (GDD §6): 130 de dano num raio de 3 m, 55 de mana, 7 s.
	MagiaPrincipal.Nome = NSLOCTEXT("Nexus", "BolaDeFogo", "Bola de Fogo");
	MagiaPrincipal.Dano = 130.f;
	MagiaPrincipal.RaioExplosao = 300.f;
	MagiaPrincipal.Alcance = 4000.f;
	MagiaPrincipal.Velocidade = 2500.f;
	MagiaPrincipal.Custo = 55.f;
	MagiaPrincipal.Recarga = 7.f;
	MagiaPrincipal.Cor = FLinearColor(1.f, 0.35f, 0.05f);
	MagiaPrincipal.Tamanho = 0.6f;
}

void UNRCombateComponent::BeginPlay()
{
	Super::BeginPlay();
	if (UNRAbilitySystemComponent* ASC = GetOwner()->FindComponentByClass<UNRAbilitySystemComponent>())
	{
		ASC->OnMorreu.AddDynamic(this, &ThisClass::AoMorrer);
	}
}

void UNRCombateComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(TimerRecomecar);
	}
	if (Hud)
	{
		Hud->RemoveFromParent();
		Hud = nullptr;
	}
	Super::EndPlay(EndPlayReason);
}

void UNRCombateComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// O herói só ganha controller e InputComponent depois de ser possuído: tenta até conseguir.
	if (!bInputLigado)
	{
		TentarLigarInput();
	}
	if (!Hud)
	{
		TentarCriarHud();
	}
	if (bInputLigado && Hud)
	{
		SetComponentTickEnabled(false);
	}
}

void UNRCombateComponent::TentarLigarInput()
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	if (!Pawn || !Pawn->IsLocallyControlled() || !Pawn->IsPlayerControlled())
	{
		return;
	}
	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(Pawn->InputComponent);
	if (!Input)
	{
		return;
	}
	// Triggered: segurar o botão esquerdo dispara de novo a cada recarga.
	if (AcaoAtaque) Input->BindAction(AcaoAtaque, ETriggerEvent::Triggered, this, &ThisClass::AoAtaque);
	if (AcaoMagiaPrincipal) Input->BindAction(AcaoMagiaPrincipal, ETriggerEvent::Started, this, &ThisClass::AoMagiaPrincipal);
	if (AcaoConsumivel1) Input->BindAction(AcaoConsumivel1, ETriggerEvent::Started, this, &ThisClass::AoConsumivel1);
	if (AcaoConsumivel2) Input->BindAction(AcaoConsumivel2, ETriggerEvent::Started, this, &ThisClass::AoConsumivel2);
	if (AcaoConsumivel3) Input->BindAction(AcaoConsumivel3, ETriggerEvent::Started, this, &ThisClass::AoConsumivel3);
	bInputLigado = true;
	UE_LOG(LogNexus, Log, TEXT("%s: teclas de combate ligadas"), *GetNameSafe(Pawn));
}

void UNRCombateComponent::TentarCriarHud()
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	APlayerController* PC = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	if (!PC || !Pawn->IsLocallyControlled())
	{
		return;
	}
	UClass* Classe = ClasseHud ? ClasseHud.Get() : UNRHudWidget::StaticClass();
	Hud = CreateWidget<UNRHudWidget>(PC, Classe);
	if (Hud)
	{
		Hud->AddToViewport(5);
	}
}

bool UNRCombateComponent::PodeAgir() const
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	if (!Pawn || Pawn->IsHidden()) // escondido = ainda no dirigível
	{
		return false;
	}
	const UNRAbilitySystemComponent* ASC = Pawn->FindComponentByClass<UNRAbilitySystemComponent>();
	return !ASC || !ASC->IsMorto();
}

bool UNRCombateComponent::UsarAtaqueBasico()
{
	return Lancar(AtaqueBasico, ProximoBasico);
}

bool UNRCombateComponent::UsarMagiaPrincipal()
{
	return Lancar(MagiaPrincipal, ProximoPrincipal);
}

bool UNRCombateComponent::UsarConsumivel(int32 Slot)
{
	if (!PodeAgir())
	{
		return false;
	}
	UNRInventoryComponent* Inventario = GetOwner()->FindComponentByClass<UNRInventoryComponent>();
	return Inventario && Inventario->UsarConsumivel(Slot);
}

float UNRCombateComponent::RecargaRestante(int32 Slot) const
{
	const UWorld* World = GetWorld();
	if (!World)
	{
		return 0.f;
	}
	const double Proximo = Slot == 0 ? ProximoBasico : ProximoPrincipal;
	return static_cast<float>(FMath::Max(0.0, Proximo - World->GetTimeSeconds()));
}

float UNRCombateComponent::TempoAteRecomecar() const
{
	const UWorld* World = GetWorld();
	return World && TimerRecomecar.IsValid() ? FMath::Max(0.f, World->GetTimerManager().GetTimerRemaining(TimerRecomecar)) : 0.f;
}

bool UNRCombateComponent::Lancar(const FNRMagiaProjetil& Magia, double& ProximoUso)
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	UWorld* World = GetWorld();
	if (!Pawn || !World || !PodeAgir())
	{
		return false;
	}
	const double Agora = World->GetTimeSeconds();
	if (Agora < ProximoUso)
	{
		return false;
	}
	UNRAbilitySystemComponent* ASC = Pawn->FindComponentByClass<UNRAbilitySystemComponent>();
	if (Magia.Custo > 0.f && (!ASC || !ASC->GastarMana(Magia.Custo)))
	{
		return false;
	}
	const float Reducao = ASC ? FMath::Clamp(ASC->GetNumericAttribute(UAS_Hero::GetReducaoRecargaAttribute()), 0.f, 0.5f) : 0.f;
	const float Poder = ASC ? ASC->GetNumericAttribute(UAS_Hero::GetPoderMagicoAttribute()) : 0.f;
	ProximoUso = Agora + Magia.Recarga * (1.f - Reducao);

	// Mira: da câmera até o que estiver no centro da tela (ou o alcance, se não houver nada).
	FVector Olho = Pawn->GetActorLocation();
	FRotator Visao = Pawn->GetActorRotation();
	if (AController* Controller = Pawn->GetController())
	{
		Controller->GetPlayerViewPoint(Olho, Visao);
	}
	FVector Alvo = Olho + Visao.Vector() * (Magia.Alcance + 1000.f);
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(NRMira), false, Pawn);
	if (World->LineTraceSingleByChannel(Hit, Olho, Alvo, ECC_Visibility, Params))
	{
		Alvo = Hit.ImpactPoint;
	}

	Pawn->SetActorRotation(FRotator(0.f, Visao.Yaw, 0.f));
	const FVector Origem = Pawn->GetActorLocation() + Pawn->GetActorForwardVector() * 60.f + FVector(0.f, 0.f, 40.f);
	FVector Direcao = (Alvo - Origem).GetSafeNormal();
	if (FVector::DotProduct(Direcao, Visao.Vector()) < 0.2f) // alvo colado no herói: segue a câmera
	{
		Direcao = Visao.Vector();
	}

	const FTransform Transform(Direcao.Rotation(), Origem);
	UClass* Classe = ClasseProjetil ? ClasseProjetil.Get() : ANRProjetilMagico::StaticClass();
	ANRProjetilMagico* Projetil = World->SpawnActorDeferred<ANRProjetilMagico>(Classe, Transform, Pawn, Pawn,
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!Projetil)
	{
		return false;
	}
	Projetil->Dano = Magia.Dano * (1.f + Poder);
	Projetil->RaioExplosao = Magia.RaioExplosao;
	if (MaterialProjetil)
	{
		Projetil->Material = MaterialProjetil;
	}
	Projetil->FinishSpawning(Transform);
	USceneComponent* Perseguir = Magia.Teleguiado > 0.f ? AlvoNaMira(Origem, Direcao, Magia.Alcance, Magia.ConeTeleguiado) : nullptr;
	Projetil->Lancar(Direcao, Magia.Velocidade, Magia.Alcance, Magia.Cor, Magia.Tamanho, Perseguir, Magia.Teleguiado);
	return true;
}

USceneComponent* UNRCombateComponent::AlvoNaMira(const FVector& Origem, const FVector& Direcao, float Alcance, float ConeGraus) const
{
	const APawn* Eu = Cast<APawn>(GetOwner());
	USceneComponent* Melhor = nullptr;
	float MelhorCos = FMath::Cos(FMath::DegreesToRadians(ConeGraus));
	for (TActorIterator<APawn> It(GetWorld()); It; ++It)
	{
		APawn* Outro = *It;
		// Sem colisão = morto (creeps) ou ainda no dirigível (heróis).
		if (Outro == Eu || Outro->IsHidden() || !Outro->GetActorEnableCollision())
		{
			continue;
		}
		const UNRAbilitySystemComponent* ASC = Outro->FindComponentByClass<UNRAbilitySystemComponent>();
		if (ASC && ASC->IsMorto())
		{
			continue;
		}
		const FVector Para = Outro->GetActorLocation() - Origem;
		const float Distancia = Para.Size();
		if (Distancia < 1.f || Distancia > Alcance)
		{
			continue;
		}
		const float Cos = FVector::DotProduct(Para / Distancia, Direcao);
		if (Cos > MelhorCos)
		{
			MelhorCos = Cos;
			Melhor = Outro->GetRootComponent();
		}
	}
	return Melhor;
}

void UNRCombateComponent::AoMorrer(AActor* Assassino)
{
	ACharacter* Heroi = Cast<ACharacter>(GetOwner());
	if (!Heroi)
	{
		return;
	}
	if (UCharacterMovementComponent* Movimento = Heroi->GetCharacterMovement())
	{
		Movimento->StopMovementImmediately();
		Movimento->DisableMovement();
	}
	if (AnimMorte)
	{
		TArray<USkeletalMeshComponent*> Malhas;
		Heroi->GetComponents(Malhas);
		for (USkeletalMeshComponent* Malha : Malhas)
		{
			Malha->PlayAnimation(AnimMorte, false);
		}
	}
	if (APlayerController* PC = Cast<APlayerController>(Heroi->GetController()))
	{
		Heroi->DisableInput(PC);
		if (TempoParaRecomecar > 0.f)
		{
			GetWorld()->GetTimerManager().SetTimer(TimerRecomecar, this, &ThisClass::Recomecar, TempoParaRecomecar, false);
		}
	}
}

void UNRCombateComponent::Recomecar()
{
	UE_LOG(LogNexus, Log, TEXT("Recomeçando a partida"));
	UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
}
