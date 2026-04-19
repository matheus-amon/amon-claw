# src/amon_claw/application/use_cases/appointment_persistence.py

from amon_claw.infrastructure.database.mongodb.client import get_mongo_db
from loguru import logger
from typing import Any
import datetime

async def save_appointment_to_db(appointment_data: dict[str, Any]) -> dict[str, Any]:
    """
    Salva dados de um agendamento concluído ou importante no MongoDB.
    Esta função seria chamada por uma 'ferramenta' do LangGraph.
    """
    db = get_mongo_db()
    appointments_collection = db.appointments # Nome da coleção

    # Adiciona um timestamp para registro
    appointment_data["created_at"] = datetime.datetime.now(datetime.timezone.utc)

    try:
        result = await appointments_collection.insert_one(appointment_data)
        logger.info(f"Agendamento salvo no MongoDB com ID: {result.inserted_id}")
        return {"status": "success", "inserted_id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Erro ao salvar agendamento no MongoDB: {e}")
        return {"status": "error", "message": str(e)}

# Exemplo de como um tool poderia ser definido (não é a implementação real da ferramenta LangGraph aqui)
# from langchain_core.tools import tool
# @tool
# async def persist_final_appointment_details(data: dict[str, Any]) -> str:
#     """Persiste os detalhes finais de um agendamento no banco de dados."""
#     response = await save_appointment_to_db(data)
#     return str(response)
