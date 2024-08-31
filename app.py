from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import SessionLocal
import uvicorn
import os

# Now the Rest Server Part
app = FastAPI(debug=True)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Create all tables


# Adding all the User and Docs Routes
from src.routes import UserRoutes, DocumentRoutes, RAGRoutes

app.include_router(UserRoutes.user_router)
app.include_router(DocumentRoutes.document_router)
app.include_router(RAGRoutes.rag_router)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get("HOST") or "localhost",
        port=os.environ.get("PORT") or 5000,
    )
