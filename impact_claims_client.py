"""
Enhanced LinkedTrust Client for Impact Claims

This module extends the existing LinkedTrust client to handle impact measurements
as LinkedClaims, utilizing the amt/unit fields for quantifiable impacts.
"""

from typing import Dict, List, Any, Optional
import logging
from linkedtrust_client import LinkedTrustClient

logger = logging.getLogger(__name__)


class ImpactClaimFormatter:
    """Formats impact measurements as LinkedClaims for LinkedTrust."""
    
    @staticmethod
    def format_impact_claim(
        subject: str,
        statement: str,
        amount: Optional[float] = None,
        unit: Optional[str] = None,
        aspect: str = "impact",
        source_uri: Optional[str] = None,
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format an impact measurement as a LinkedClaim.
        
        Args:
            subject: The entity making the impact (URI or name)
            statement: Description of the impact
            amount: Quantifiable amount of impact (uses 'amt' field)
            unit: Unit of measurement
            aspect: Type of impact (e.g., "impact:social", "impact:environmental")
            source_uri: Source document or report URI
            confidence: Confidence score (0-1)
            metadata: Additional metadata
            
        Returns:
            Formatted LinkedClaim ready for submission
        """
        claim = {
            "subject": subject,
            "claim": "impact",
            "statement": statement,
            "aspect": aspect,
            "confidence": confidence
        }
        
        # Add quantifiable measurements if provided
        if amount is not None:
            claim["amt"] = amount
        if unit:
            claim["unit"] = unit
            
        # Add source if provided
        if source_uri:
            claim["sourceURI"] = source_uri
            claim["howKnown"] = "WEB_DOCUMENT"
            
        # Add any additional metadata
        if metadata:
            claim.update(metadata)
            
        return claim
    
    @staticmethod
    def extract_impact_claims_from_report(
        report_data: Dict[str, Any],
        source_uri: str
    ) -> List[Dict[str, Any]]:
        """
        Extract multiple impact claims from a parsed report.
        
        Args:
            report_data: Parsed report data containing impact measurements
            source_uri: URI of the source report
            
        Returns:
            List of formatted LinkedClaims
        """
        claims = []
        
        # Extract organization/subject
        subject = report_data.get("organization", report_data.get("subject", "Unknown"))
        
        # Process different types of impacts
        if "impacts" in report_data:
            for impact in report_data["impacts"]:
                claim = ImpactClaimFormatter.format_impact_claim(
                    subject=subject,
                    statement=impact.get("description", ""),
                    amount=impact.get("amount"),
                    unit=impact.get("unit"),
                    aspect=f"impact:{impact.get('type', 'general')}",
                    source_uri=source_uri,
                    confidence=impact.get("confidence", 0.8)
                )
                claims.append(claim)
        
        # Process environmental impacts
        if "environmental" in report_data:
            env_data = report_data["environmental"]
            if "co2_reduced" in env_data:
                claims.append(ImpactClaimFormatter.format_impact_claim(
                    subject=subject,
                    statement=f"Reduced CO2 emissions by {env_data['co2_reduced']} {env_data.get('co2_unit', 'tons')}",
                    amount=env_data["co2_reduced"],
                    unit=env_data.get("co2_unit", "tons"),
                    aspect="impact:environmental:carbon",
                    source_uri=source_uri
                ))
                
        # Process social impacts
        if "social" in report_data:
            social_data = report_data["social"]
            if "people_helped" in social_data:
                claims.append(ImpactClaimFormatter.format_impact_claim(
                    subject=subject,
                    statement=social_data.get("description", f"Helped {social_data['people_helped']} people"),
                    amount=social_data["people_helped"],
                    unit="people",
                    aspect="impact:social",
                    source_uri=source_uri
                ))
                
        return claims


class EnhancedLinkedTrustClient(LinkedTrustClient):
    """Enhanced client with impact claim support."""
    
    def submit_impact_claim(
        self,
        subject: str,
        statement: str,
        amount: Optional[float] = None,
        unit: Optional[str] = None,
        aspect: str = "impact",
        source_uri: Optional[str] = None,
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit an impact measurement as a LinkedClaim.
        
        Args:
            subject: The entity making the impact
            statement: Description of the impact
            amount: Quantifiable amount of impact
            unit: Unit of measurement
            aspect: Type of impact
            source_uri: Source document URI
            confidence: Confidence score
            metadata: Additional metadata
            
        Returns:
            API response data
        """
        claim = ImpactClaimFormatter.format_impact_claim(
            subject=subject,
            statement=statement,
            amount=amount,
            unit=unit,
            aspect=aspect,
            source_uri=source_uri,
            confidence=confidence,
            metadata=metadata
        )
        
        return self.submit_claim(claim)
    
    def submit_impact_report(
        self,
        report_data: Dict[str, Any],
        source_uri: str
    ) -> List[Dict[str, Any]]:
        """
        Submit all impact claims extracted from a report.
        
        Args:
            report_data: Parsed report data
            source_uri: URI of the source report
            
        Returns:
            List of API responses
        """
        claims = ImpactClaimFormatter.extract_impact_claims_from_report(
            report_data,
            source_uri
        )
        
        return self.submit_claims_batch(claims)


# Example usage and integration
if __name__ == "__main__":
    # Initialize enhanced client
    client = EnhancedLinkedTrustClient()
    
    # Example 1: Submit a single impact claim
    response = client.submit_impact_claim(
        subject="Gates Foundation",
        statement="Provided clean water access to communities in Africa",
        amount=50000,
        unit="people",
        aspect="impact:social:water",
        source_uri="https://gatesfoundation.org/report2024",
        confidence=0.95
    )
    print(f"Single claim response: {response}")
    
    # Example 2: Submit impact report
    example_report = {
        "organization": "Tesla Inc",
        "impacts": [
            {
                "type": "environmental",
                "description": "Reduced carbon emissions through electric vehicle adoption",
                "amount": 5000000,
                "unit": "tons CO2",
                "confidence": 0.9
            },
            {
                "type": "social",
                "description": "Created sustainable transportation jobs",
                "amount": 50000,
                "unit": "jobs",
                "confidence": 0.85
            }
        ]
    }
    
    responses = client.submit_impact_report(
        example_report,
        "https://tesla.com/impact-report-2024"
    )
    print(f"Batch submission results: {len(responses)} claims submitted")
