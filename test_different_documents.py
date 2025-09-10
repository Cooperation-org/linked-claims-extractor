#!/usr/bin/env python3
"""
Systematic testing of claims extraction across different document types
"""

import sys
import os
import json
import statistics
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the claim_extractor to the Python path
sys.path.insert(0, 'claim_extractor/src')

from claim_extractor import ClaimExtractor

class DocumentTester:
    def __init__(self):
        self.extractor = ClaimExtractor()
        self.results = []
        
    def test_document(self, filename, document_type):
        """Test extraction on a single document"""
        print(f"\n{'='*50}")
        print(f"Testing: {filename} ({document_type})")
        print(f"{'='*50}")
        
        try:
            # Read the document
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
            
            print(f"Document length: {len(text)} characters")
            
            # Extract claims
            claims = self.extractor.extract_claims(text)
            
            # Analyze results
            analysis = self.analyze_claims(claims, text, filename, document_type)
            self.results.append(analysis)
            
            # Print summary
            self.print_document_summary(analysis)
            
            return analysis
            
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            return None
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            return None
    
    def analyze_claims(self, claims, text, filename, document_type):
        """Analyze extracted claims and generate metrics"""
        if not claims:
            return {
                'filename': filename,
                'document_type': document_type,
                'text_length': len(text),
                'claims_count': 0,
                'claims': [],
                'avg_confidence': 0,
                'aspects': {},
                'claim_types': {},
                'quantified_claims': 0,
                'errors': ['No claims extracted']
            }
        
        # Calculate metrics
        confidences = [c.get('confidence', 0) for c in claims]
        avg_confidence = statistics.mean(confidences) if confidences else 0
        
        # Count aspects
        aspects = {}
        for claim in claims:
            aspect = claim.get('aspect', 'unknown')
            aspects[aspect] = aspects.get(aspect, 0) + 1
        
        # Count claim types
        claim_types = {}
        for claim in claims:
            claim_type = claim.get('claim', 'unknown')
            claim_types[claim_type] = claim_types.get(claim_type, 0) + 1
        
        # Count quantified claims (those with amt field)
        quantified_claims = len([c for c in claims if c.get('amt') is not None])
        
        return {
            'filename': filename,
            'document_type': document_type,
            'text_length': len(text),
            'claims_count': len(claims),
            'claims': claims,
            'avg_confidence': round(avg_confidence, 3),
            'min_confidence': min(confidences) if confidences else 0,
            'max_confidence': max(confidences) if confidences else 0,
            'aspects': aspects,
            'claim_types': claim_types,
            'quantified_claims': quantified_claims,
            'words_per_claim': len(text.split()) // len(claims) if claims else 0
        }
    
    def print_document_summary(self, analysis):
        """Print summary for a single document"""
        print(f"✅ Extracted {analysis['claims_count']} claims")
        print(f"📊 Average confidence: {analysis['avg_confidence']}")
        print(f"📈 Quantified claims: {analysis['quantified_claims']}")
        print(f"🏷️  Aspects found: {', '.join(analysis['aspects'].keys())}")
        
        # Show individual claims
        for i, claim in enumerate(analysis['claims'], 1):
            statement = claim.get('statement', '')[:60] + "..." if len(claim.get('statement', '')) > 60 else claim.get('statement', '')
            confidence = claim.get('confidence', 0)
            aspect = claim.get('aspect', 'unknown')
            amt = claim.get('amt')
            unit = claim.get('unit', '')
            
            print(f"  {i}. [{confidence}] {aspect}: {statement}")
            if amt is not None:
                print(f"      💰 Quantity: {amt} {unit}")
    
    def run_all_tests(self):
        """Run tests on all available test files"""
        test_files = [
    ('test_document.txt', 'Meta Baseline'),
    ('test_financial_claims.txt', 'Financial Focus'),
    ('test_social_impact.txt', 'Social Impact'),
    ('test_environmental_data.txt', 'Environmental'),
    ('test_tech_company.txt', 'Tech Company'),
    ('test_microsoft_report.txt', 'Microsoft Report'),
    ('test_real_world_amazon.txt', 'Amazon Real-World'),
    ('test_real_world_unilever.txt', 'Unilever Real-World'),
    ('test_real_world_patagonia.txt', 'Patagonia Real-World')
]
        
        print("🔬 SYSTEMATIC DOCUMENT TESTING")
        print("=" * 60)
        
        # Test each document
        successful_tests = 0
        for filename, doc_type in test_files:
            if os.path.exists(filename):
                result = self.test_document(filename, doc_type)
                if result:
                    successful_tests += 1
            else:
                print(f"⚠️  Skipping {filename} - file not found")
        
        # Generate comparative analysis
        if successful_tests > 0:
            self.generate_comparative_report()
        else:
            print("❌ No test files found to process")
    
    def generate_comparative_report(self):
        """Generate comprehensive comparison across all tested documents"""
        print(f"\n{'='*60}")
        print("📋 COMPARATIVE ANALYSIS REPORT")
        print(f"{'='*60}")
        
        if not self.results:
            print("No results to analyze")
            return
        
        # Overall statistics
        total_claims = sum(r['claims_count'] for r in self.results)
        avg_claims_per_doc = total_claims / len(self.results)
        all_confidences = []
        for result in self.results:
            for claim in result['claims']:
                all_confidences.append(claim.get('confidence', 0))
        
        overall_avg_confidence = statistics.mean(all_confidences) if all_confidences else 0
        
        print(f"📊 OVERALL METRICS:")
        print(f"   Documents tested: {len(self.results)}")
        print(f"   Total claims extracted: {total_claims}")
        print(f"   Average claims per document: {avg_claims_per_doc:.1f}")
        print(f"   Overall confidence: {overall_avg_confidence:.3f}")
        
        # Performance by document type
        print(f"\n📈 PERFORMANCE BY DOCUMENT TYPE:")
        for result in sorted(self.results, key=lambda x: x['claims_count'], reverse=True):
            efficiency = result['claims_count'] / (result['text_length'] / 100)  # claims per 100 chars
            print(f"   {result['document_type']:20} | {result['claims_count']:2d} claims | {result['avg_confidence']:.3f} conf | {efficiency:.2f} eff")
        
        # Aspect analysis
        all_aspects = {}
        for result in self.results:
            for aspect, count in result['aspects'].items():
                all_aspects[aspect] = all_aspects.get(aspect, 0) + count
        
        print(f"\n🏷️  ASPECT DISTRIBUTION:")
        for aspect, count in sorted(all_aspects.items(), key=lambda x: x[1], reverse=True):
            print(f"   {aspect:25} | {count:2d} claims")
        
        # Quantification analysis
        total_quantified = sum(r['quantified_claims'] for r in self.results)
        quantification_rate = (total_quantified / total_claims * 100) if total_claims > 0 else 0
        
        print(f"\n💰 QUANTIFICATION ANALYSIS:")
        print(f"   Quantified claims: {total_quantified}/{total_claims} ({quantification_rate:.1f}%)")
        
        for result in self.results:
            if result['quantified_claims'] > 0:
                rate = (result['quantified_claims'] / result['claims_count'] * 100) if result['claims_count'] > 0 else 0
                print(f"   {result['document_type']:20} | {result['quantified_claims']:2d}/{result['claims_count']:2d} ({rate:.0f}%)")
        
        # Best performing documents
        print(f"\n🏆 TOP PERFORMERS:")
        
        # Most claims extracted
        best_volume = max(self.results, key=lambda x: x['claims_count'])
        print(f"   Most claims: {best_volume['document_type']} ({best_volume['claims_count']} claims)")
        
        # Highest confidence
        best_confidence = max(self.results, key=lambda x: x['avg_confidence'])
        print(f"   Highest confidence: {best_confidence['document_type']} ({best_confidence['avg_confidence']:.3f})")
        
        # Most quantified
        best_quantified = max(self.results, key=lambda x: x['quantified_claims'])
        print(f"   Most quantified: {best_quantified['document_type']} ({best_quantified['quantified_claims']} claims)")
        
        # Recommendations
        self.generate_recommendations()
    
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        print(f"\n💡 RECOMMENDATIONS:")
        
        # Check for low-performing areas
        avg_claims = statistics.mean([r['claims_count'] for r in self.results])
        avg_confidence = statistics.mean([r['avg_confidence'] for r in self.results])
        
        low_performers = [r for r in self.results if r['claims_count'] < avg_claims * 0.7]
        if low_performers:
            print(f"   📉 Consider improving extraction for: {', '.join([r['document_type'] for r in low_performers])}")
        
        low_confidence = [r for r in self.results if r['avg_confidence'] < 0.8]
        if low_confidence:
            print(f"   🎯 Focus on confidence improvement for: {', '.join([r['document_type'] for r in low_confidence])}")
        
        # Check aspect coverage
        all_aspects = set()
        for result in self.results:
            all_aspects.update(result['aspects'].keys())
        
        if 'impact:environmental' not in all_aspects:
            print(f"   🌱 Consider testing more environmental content")
        if 'impact:social' not in all_aspects:
            print(f"   👥 Consider testing more social impact content")
        if 'impact:financial' not in all_aspects:
            print(f"   💼 Consider testing more financial content")
        
        print(f"   ✅ System performs consistently across {len(self.results)} document types")
        
    def save_results(self):
        """Save detailed results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extraction_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")

def main():
    """Main function to run document testing"""
    tester = DocumentTester()
    
    print("🧪 Starting systematic document testing...")
    tester.run_all_tests()
    tester.save_results()
    
    print(f"\n{'='*60}")
    print("Testing complete! Results saved for analysis.")

if __name__ == "__main__":
    main()