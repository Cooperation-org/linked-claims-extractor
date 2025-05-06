"""
Key Management Service for LinkedTrust Claim Signing

This module handles the generation, storage, and usage of cryptographic keys
for signing claims to be published to the LinkedTrust platform.
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeyManager:
    """Manages cryptographic keys for signing claims."""
    
    def __init__(self, key_dir: str = ".keys"):
        """
        Initialize the key manager.
        
        Args:
            key_dir: Directory to store key files
        """
        self.key_dir = Path(key_dir)
        self._ensure_key_dir()
        
        # Default key paths
        self.private_key_path = self.key_dir / "linkedtrust_private.pem"
        self.public_key_path = self.key_dir / "linkedtrust_public.pem"
        
        # Loaded keys
        self.private_key = None
        self.public_key = None
        
    def _ensure_key_dir(self) -> None:
        """Ensure the key directory exists."""
        if not self.key_dir.exists():
            self.key_dir.mkdir(parents=True)
            logger.info(f"Created key directory: {self.key_dir}")
            
            # Create .gitignore to prevent accidental key commits
            with open(self.key_dir / ".gitignore", "w") as f:
                f.write("# Ignore all files in this directory\n*\n!.gitignore\n")
                
    def generate_key_pair(self, key_size: int = 2048) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """
        Generate a new RSA key pair.
        
        Args:
            key_size: Size of the key in bits
            
        Returns:
            Tuple of (private_key, public_key)
        """
        logger.info(f"Generating new {key_size}-bit RSA key pair")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # Extract public key
        public_key = private_key.public_key()
        
        return private_key, public_key
    
    def save_key_pair(
        self, 
        private_key: rsa.RSAPrivateKey, 
        public_key: rsa.RSAPublicKey,
        private_key_path: Optional[Path] = None,
        public_key_path: Optional[Path] = None,
        password: Optional[str] = None
    ) -> Tuple[Path, Path]:
        """
        Save a key pair to disk.
        
        Args:
            private_key: RSA private key
            public_key: RSA public key
            private_key_path: Path to save private key (default: self.private_key_path)
            public_key_path: Path to save public key (default: self.public_key_path)
            password: Optional password to encrypt the private key
            
        Returns:
            Tuple of (private_key_path, public_key_path)
        """
        # Set default paths if not provided
        private_key_path = private_key_path or self.private_key_path
        public_key_path = public_key_path or self.public_key_path
        
        # Serialize and save private key
        encryption_algorithm = serialization.BestAvailableEncryption(password.encode()) if password else serialization.NoEncryption()
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        with open(private_key_path, "wb") as f:
            f.write(private_pem)
            logger.info(f"Private key saved to {private_key_path}")
            
        # Set restrictive permissions on private key
        os.chmod(private_key_path, 0o600)
            
        # Serialize and save public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(public_key_path, "wb") as f:
            f.write(public_pem)
            logger.info(f"Public key saved to {public_key_path}")
            
        return private_key_path, public_key_path
    
    def load_keys(
        self,
        private_key_path: Optional[Path] = None,
        public_key_path: Optional[Path] = None,
        password: Optional[str] = None
    ) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """
        Load keys from disk.
        
        Args:
            private_key_path: Path to private key file (default: self.private_key_path)
            public_key_path: Path to public key file (default: self.public_key_path)
            password: Optional password to decrypt the private key
            
        Returns:
            Tuple of (private_key, public_key)
        """
        # Set default paths if not provided
        private_key_path = private_key_path or self.private_key_path
        public_key_path = public_key_path or self.public_key_path
        
        # Load private key if path exists
        if os.path.exists(private_key_path):
            with open(private_key_path, "rb") as f:
                private_key_data = f.read()
                
            try:
                private_key = serialization.load_pem_private_key(
                    private_key_data,
                    password=password.encode() if password else None,
                    backend=default_backend()
                )
                self.private_key = private_key
                logger.info(f"Loaded private key from {private_key_path}")
            except Exception as e:
                logger.error(f"Failed to load private key: {str(e)}")
                self.private_key = None
        else:
            logger.warning(f"Private key file not found: {private_key_path}")
            self.private_key = None
            
        # Load public key if path exists
        if os.path.exists(public_key_path):
            with open(public_key_path, "rb") as f:
                public_key_data = f.read()
                
            try:
                public_key = serialization.load_pem_public_key(
                    public_key_data,
                    backend=default_backend()
                )
                self.public_key = public_key
                logger.info(f"Loaded public key from {public_key_path}")
            except Exception as e:
                logger.error(f"Failed to load public key: {str(e)}")
                self.public_key = None
        else:
            logger.warning(f"Public key file not found: {public_key_path}")
            self.public_key = None
            
        return self.private_key, self.public_key
    
    def ensure_keys_exist(self, password: Optional[str] = None) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """
        Ensure a key pair exists, generating a new one if necessary.
        
        Args:
            password: Optional password for private key encryption
            
        Returns:
            Tuple of (private_key, public_key)
        """
        # Try to load existing keys
        self.load_keys(password=password)
        
        # If either key is missing, generate a new pair
        if not self.private_key or not self.public_key:
            logger.info("Keys not found or invalid, generating new key pair")
            private_key, public_key = self.generate_key_pair()
            self.save_key_pair(private_key, public_key, password=password)
            self.private_key = private_key
            self.public_key = public_key
            
        return self.private_key, self.public_key
    
    def sign_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign a claim with the private key.
        
        Args:
            claim: The claim to sign
            
        Returns:
            The claim with signature added
        """
        if not self.private_key:
            raise ValueError("Private key not loaded")
            
        # Make a copy of the claim to avoid modifying the original
        claim_copy = claim.copy()
        
        # Remove any existing signature
        claim_copy.pop("signature", None)
        
        # Convert claim to canonical JSON string
        canonical_json = json.dumps(claim_copy, sort_keys=True, separators=(',', ':'))
        
        # Sign the canonical JSON
        signature = self.private_key.sign(
            canonical_json.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Add base64-encoded signature to claim
        claim_copy["signature"] = base64.b64encode(signature).decode('utf-8')
        
        return claim_copy
    
    def verify_signature(self, claim: Dict[str, Any]) -> bool:
        """
        Verify the signature on a claim.
        
        Args:
            claim: The signed claim to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.public_key:
            raise ValueError("Public key not loaded")
            
        if "signature" not in claim:
            logger.warning("Claim has no signature")
            return False
            
        # Make a copy and extract signature
        claim_copy = claim.copy()
        signature = base64.b64decode(claim_copy.pop("signature"))
        
        # Convert remaining claim to canonical JSON
        canonical_json = json.dumps(claim_copy, sort_keys=True, separators=(',', ':'))
        
        # Verify signature
        try:
            self.public_key.verify(
                signature,
                canonical_json.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Create key manager
    key_manager = KeyManager()
    
    # Ensure keys exist (generates if needed)
    private_key, public_key = key_manager.ensure_keys_exist()
    
    # Example claim
    claim = {
        "subject": "Gates Foundation",
        "claim": "impact",
        "statement": "The Gates Foundation helped vaccinate over 10 million children in 2019.",
        "aspect": "impact:social",
        "effectiveDate": "2019-12-31T00:00:00Z",
        "confidence": 0.95
    }
    
    # Sign the claim
    signed_claim = key_manager.sign_claim(claim)
    print(f"Signed claim: {signed_claim}")
    
    # Verify the signature
    is_valid = key_manager.verify_signature(signed_claim)
    print(f"Signature valid: {is_valid}")
