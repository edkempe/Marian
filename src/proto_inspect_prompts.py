#!/usr/bin/env python3
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate
import pandas as pd
from datetime import datetime

# SQLAlchemy setup
Base = declarative_base()

class Prompt(Base):
    """SQLAlchemy model for prompts"""
    __tablename__ = 'prompts'
    
    prompt_id = Column(String, primary_key=True)
    prompt_text = Column(String, nullable=False)
    version_number = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    model_name = Column(String)
    max_tokens = Column(Integer)
    description = Column(String)
    script_name = Column(String)
    expected_response_format = Column(String)
    required_input_fields = Column(String)
    token_estimate = Column(Integer)
    times_used = Column(Integer, default=0)
    average_confidence_score = Column(Float)
    average_response_time_ms = Column(Float)
    failure_rate = Column(Float, default=0.0)

def inspect_prompts_db():
    """Inspect the prompts database."""
    # Create SQLAlchemy engine and session
    engine = create_engine('sqlite:///data/prompts.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all prompts
        prompts = session.query(Prompt).order_by(Prompt.created_date.desc()).all()
        
        if not prompts:
            print("No prompts found in database")
            return
        
        # Basic info
        basic_info = pd.DataFrame([{
            'ID': prompt.prompt_id,
            'Version': prompt.version_number,
            'Script': prompt.script_name,
            'Model': prompt.model_name,
            'Active': prompt.active,
            'Created': prompt.created_date
        } for prompt in prompts])
        
        print("\n=== Prompts Overview ===")
        print(tabulate(basic_info, headers='keys', tablefmt='pretty'))
        
        # Detailed view of each prompt
        for prompt in prompts:
            print(f"\n=== Prompt Details for Version {prompt.version_number} ===")
            print(f"Description: {prompt.description}")
            print(f"Script: {prompt.script_name}")
            print(f"Model: {prompt.model_name}")
            print(f"Max Tokens: {prompt.max_tokens}")
            print(f"Token Estimate: {prompt.token_estimate}")
            
            print("\nPrompt Text:")
            print("-" * 80)
            print(prompt.prompt_text)
            print("-" * 80)
            
            print("\nPerformance Metrics:")
            print(f"Times Used: {prompt.times_used}")
            print(f"Average Confidence: {prompt.average_confidence_score:.2f}" if prompt.average_confidence_score else "Average Confidence: N/A")
            print(f"Average Response Time: {prompt.average_response_time_ms:.0f}ms" if prompt.average_response_time_ms else "Average Response Time: N/A")
            print(f"Failure Rate: {prompt.failure_rate*100:.1f}%" if prompt.failure_rate is not None else "Failure Rate: N/A")
            
            if prompt.expected_response_format:
                print("\nExpected Response Format:")
                print(prompt.expected_response_format)
                
            if prompt.required_input_fields:
                print("\nRequired Input Fields:")
                print(prompt.required_input_fields)
                
    finally:
        session.close()

if __name__ == "__main__":
    inspect_prompts_db()
