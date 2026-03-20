#!/usr/bin/env python3
"""
Training script for the LLM implementation
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import numpy as np
from main import LLM
import os

class TextDataset(Dataset):
    """Simple text dataset for training"""
    
    def __init__(self, text_data, vocab_size, seq_len=64):
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        
        # Simple tokenization - in practice, you'd use a proper tokenizer
        self.tokens = [ord(c) % vocab_size for c in text_data]
        
    def __len__(self):
        return len(self.tokens) - self.seq_len
    
    def __getitem__(self, idx):
        # Create input and target sequences
        input_seq = torch.tensor(self.tokens[idx:idx+self.seq_len])
        target_seq = torch.tensor(self.tokens[idx+1:idx+self.seq_len+1])
        return input_seq, target_seq

def create_sample_data():
    """Create sample training data"""
    # Simple text data for demonstration
    sample_text = "The quick brown fox jumps over the lazy dog. " * 1000
    return sample_text

def train_llm():
    """Train the LLM model"""
    print("Starting LLM training...")
    
    # Model parameters
    vocab_size = 1000
    d_model = 128
    n_heads = 4
    n_layers = 2
    d_ff = 256
    max_seq_len = 64
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create sample data
    text_data = create_sample_data()
    dataset = TextDataset(text_data, vocab_size, max_seq_len)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
    
    # Create model
    model = LLM(
        vocab_size=vocab_size,
        d_model=d_model,
        n_heads=n_heads,
        n_layers=n_layers,
        d_ff=d_ff,
        max_seq_len=max_seq_len
    ).to(device)
    
    # Optimizer and loss
    optimizer = optim.Adam(model.parameters(), lr=0.001, betas=(0.9, 0.98), eps=1e-9)
    # No padding is used in this toy dataset, so don't ignore real token id 0.
    criterion = nn.CrossEntropyLoss()
    
    # Training loop
    num_epochs = 5
    for epoch in range(num_epochs):
        avg_loss = train_model(model, dataloader, optimizer, criterion, device)
        print(f"Epoch {epoch+1}/{num_epochs}, Average Loss: {avg_loss:.4f}")
    
    # Save model
    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/llm_model.pth")
    print("Model saved to models/llm_model.pth")
    
    # Test generation
    model.eval()
    with torch.no_grad():
        # Create a simple prompt
        prompt = torch.tensor([[1, 2, 3]], dtype=torch.long).to(device)
        generated = model.generate(prompt, max_length=20, temperature=0.8)
        print(f"Generated text (tokens): {generated[0].tolist()}")

def train_model(model, data_loader, optimizer, criterion, device):
    """Training loop for the LLM"""
    model.train()
    total_loss = 0
    
    for batch_idx, (inputs, targets) in enumerate(data_loader):
        inputs, targets = inputs.to(device), targets.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs.reshape(-1, outputs.size(-1)), targets.reshape(-1))
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        
        optimizer.step()
        total_loss += loss.item()
        
        if batch_idx % 100 == 0:
            print(f"Batch {batch_idx}, Loss: {loss.item():.4f}")
    
    return total_loss / len(data_loader)

if __name__ == "__main__":
    train_llm()