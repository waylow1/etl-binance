# ETL Binance - Streaming Trades vers Kafka

## Description

Ce projet met en place un pipeline **ETL** basique pour consommer en temps réel les trades du symbole `BTCUSDT` depuis le WebSocket public de Binance, puis publier ces données dans un topic **Kafka**.
L’objectif est de démontrer une architecture data stream complète avec une infra légère.

---

## Architecture & Pipeline

```
    BinanceWebSocket --> Provider[Provider (FastAPI + Kafka Producer)]
    Provider --> KafkaCluster[Kafka (Broker + ZooKeeper)]
    KafkaCluster --> Consumer[Consumer (ex: Dashboard, Analyse)]
```

- **Binance WebSocket** : source des données streaming (endpoint `wss://stream.binance.com:9443/ws/btcusdt@trade`)

- **Provider** : microservice Python (FastAPI) qui consomme le WebSocket, extrait les informations clés et publie dans Kafka.

- **Kafka** : broker de messages distribué, stocke et distribue les événements.

- **Consumer** : front streamlit ou autre service qui consomme les messages de Kafka pour affichage ou analyse.
