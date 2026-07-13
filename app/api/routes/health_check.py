from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus

router = APIRouter()

@router.get('/')
def health_check():
    return 'hello!'