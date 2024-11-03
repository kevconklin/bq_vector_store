# BigQuery Vector Store Example

Example Retrieval Augmented Generation (RAG) application using Google Cloud for relevant services; BigQuery as a Vector Store and Vertex AI for model services.

See reference [Medium article](https://medium.com/@kevinconklin_17818/using-bigquery-as-a-vector-store-b1ca91371854) for more detailed walkthrough

## Running the application

To run the application, create a `.env` in the root directory using the `.env.example` file as reference. Ensure all Google Cloud APIs are enabled and logged in via the Google Cloud CLI.

The repo below should run with the below command from the root directory. 

```
docker compose up --build
```

# Application Structure

```
└── bq_vector_store
    └── client
        └── app.py
        └── Dockerfile
        └── requirements.txt
    └── server
        └── app.py
        └── Dockerfile
        └── requirements.txt
    └── .env
    └── .env.example
    └── .gitignore
    └── docker-compose.yaml
    └── README.md
```
