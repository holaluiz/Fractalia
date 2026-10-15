#pragma once

#include "CoreMinimal.h"
#include "NRMagiaTypes.generated.h"

// Configuração das magias do herói (GDD §4.1 e §6). Distâncias em cm, tempos em segundos.
// Ficam aqui, fora do UNRCombateComponent, porque os atores das magias (estrutura, chuva) também as usam.

/** Uma magia que dispara um projétil (ataque básico, Bola de Fogo). */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRMagiaProjetil
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") FText Nome;
	/** Dano base; é multiplicado por (1 + Poder Mágico) de quem lança. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Dano = 60.f;
	/** 0 = acerta só o alvo. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float RaioExplosao = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Alcance = 3500.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Velocidade = 4000.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Custo = 0.f;
	/** Antes da Redução de Recarga. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Recarga = 1.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") FLinearColor Cor = FLinearColor(0.6f, 0.4f, 1.f);
	/** Diâmetro da esfera em voo, em metros. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Tamanho = 0.25f;
	/** Aceleração em cm/s² na direção do inimigo mais perto da mira (até ConeTeleguiado graus). 0 = reto. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Teleguiado = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float ConeTeleguiado = 12.f;
	/**
	 * Segundos de chão em chamas no raio da explosão (mutação da Bola de Fogo, GDD §7.4: "deixa chão em chamas por 3 s").
	 * 0 = sem chamas.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float DuracaoChamas = 0.f;
	/** O GDD não dá o número; usa os 20/s da Chuva de Meteoros. Também multiplica pelo Poder Mágico. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float DanoChamasPorSegundo = 20.f;
};

/** Magia de campo que ergue uma estrutura no chão, de frente para quem lança (Muralha de Gelo, GDD §6.2 e §6.3). */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRMagiaEstrutura
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") FText Nome;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Custo = 50.f;
	/** Antes da Redução de Recarga. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Recarga = 12.f;
	/** Distância máxima (no plano) entre o herói e o centro da estrutura. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Alcance = 1500.f;
	/** Mais perto que isso, a estrutura é empurrada para frente (para não nascer em cima do herói). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float DistanciaMinima = 250.f;
	/** Espessura (X), largura (Y) e altura (Z), em cm. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") FVector Tamanho = FVector(60.f, 600.f, 350.f);
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Vida = 400.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Duracao = 6.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") FLinearColor Cor = FLinearColor(0.35f, 0.85f, 1.f);
};

/**
 * Ultimate de área com aviso no chão (Chuva de Meteoros, GDD §6.4): depois de Aviso segundos caem Meteoros
 * meteoros espalhados na área; cada alvo sofre no máximo um deles. O chão fica em chamas por DuracaoChamas.
 */
USTRUCT(BlueprintType)
struct NEXUSROYALE_API FNRMagiaChuva
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") FText Nome;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Custo = 120.f;
	/** Antes da Redução de Recarga. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Recarga = 80.f;
	/** Distância máxima (no plano) entre o herói e o centro da área. O GDD não diz; 30 m é chute. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Alcance = 3000.f;
	/** "Área de 8 m" no GDD, lida como 8 m de diâmetro (o GDD escreve "raio de" quando é raio). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float RaioArea = 400.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia", meta = (ClampMin = "1")) int32 Meteoros = 3;
	/** Dano base de cada meteoro; é multiplicado por (1 + Poder Mágico). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float DanoMeteoro = 120.f;
	/** Raio da explosão de cada meteoro. Com 3 meteoros a meio raio do centro, 0,875 × RaioArea cobre a área toda. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float RaioMeteoro = 350.f;
	/** Tempo de aviso no chão até o primeiro meteoro cair. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float Aviso = 1.f;
	/** Intervalo entre um meteoro e o próximo. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float IntervaloMeteoros = 0.2f;
	/** Contada a partir do primeiro meteoro. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float DuracaoChamas = 4.f;
	/** O GDD não dá o número do chão em chamas; usa os 20/s da vegetação queimando (§6.5). Também multiplica pelo Poder Mágico. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") float DanoChamasPorSegundo = 20.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Magia") FLinearColor Cor = FLinearColor(1.f, 0.35f, 0.05f);
};
