#!/usr/bin/env python3
"""
Deep analysis of claims extraction patterns to identify optimization opportunities
"""

import json
import statistics
import re
from collections import defaultdict, Counter
import glob

class ExtractionAnalyzer:
    def __init__(self, results_file):
        """Load extraction results from JSON file"""
        with open(results_file, 'r') as f:
            self.results = json.load(f)
        
        # Flatten all claims for analysis
        self.all_claims = []
        for result in self.results:
            for claim in result['claims']:
                claim['source_doc'] = result['document_type']
                claim['text_length'] = result['text_length']
                self.all_claims.append(claim)
    
    def analyze_confidence_patterns(self):
        """Analyze confidence score patterns across different factors"""
        print("CONFIDENCE SCORE ANALYSIS")
        print("=" * 50)
        
        # By document type
        conf_by_doc = defaultdict(list)
        for result in self.results:
            for claim in result['claims']:
                conf_by_doc[result['document_type']].append(claim.get('confidence', 0))
        
        print("Confidence by Document Type:")
        for doc_type, confidences in sorted(conf_by_doc.items(), key=lambda x: statistics.mean(x[1]), reverse=True):
            avg_conf = statistics.mean(confidences)
            std_conf = statistics.stdev(confidences) if len(confidences) > 1 else 0
            print(f"  {doc_type:20} | Avg: {avg_conf:.3f} | Std: {std_conf:.3f} | Range: {min(confidences):.1f}-{max(confidences):.1f}")
        
        # By aspect
        conf_by_aspect = defaultdict(list)
        for claim in self.all_claims:
            conf_by_aspect[claim.get('aspect', 'unknown')].append(claim.get('confidence', 0))
        
        print("\nConfidence by Aspect:")
        for aspect, confidences in sorted(conf_by_aspect.items(), key=lambda x: statistics.mean(x[1]), reverse=True):
            if len(confidences) >= 2:  # Only show aspects with multiple claims
                avg_conf = statistics.mean(confidences)
                print(f"  {aspect:25} | Avg: {avg_conf:.3f} | Count: {len(confidences)}")
        
        # Identify low confidence claims for investigation
        low_confidence = [c for c in self.all_claims if c.get('confidence', 0) < 0.8]
        if low_confidence:
            print(f"\nLow Confidence Claims (< 0.8):")
            for claim in low_confidence:
                statement = claim.get('statement', '')[:80] + "..." if len(claim.get('statement', '')) > 80 else claim.get('statement', '')
                print(f"  [{claim.get('confidence', 0):.1f}] {claim['source_doc']}: {statement}")
    
    def analyze_quantification_patterns(self):
        """Analyze what factors lead to successful quantification"""
        print("\n\nQUANTIFICATION PATTERN ANALYSIS")
        print("=" * 50)
        
        quantified = [c for c in self.all_claims if c.get('amt') is not None]
        unquantified = [c for c in self.all_claims if c.get('amt') is None]
        
        print(f"Quantified claims: {len(quantified)}/{len(self.all_claims)} ({len(quantified)/len(self.all_claims)*100:.1f}%)")
        
        # By document type
        quant_by_doc = {}
        for result in self.results:
            total = len(result['claims'])
            quantified_count = result['quantified_claims']
            rate = (quantified_count / total * 100) if total > 0 else 0
            quant_by_doc[result['document_type']] = {
                'rate': rate,
                'count': quantified_count,
                'total': total
            }
        
        print("\nQuantification Rate by Document Type:")
        for doc_type, stats in sorted(quant_by_doc.items(), key=lambda x: x[1]['rate'], reverse=True):
            print(f"  {doc_type:20} | {stats['count']:2d}/{stats['total']:2d} ({stats['rate']:5.1f}%)")
        
        # Analyze statement characteristics
        self.analyze_quantification_triggers(quantified, unquantified)
        
        # Missing quantification opportunities
        self.identify_missed_quantifications(unquantified)
    
    def analyze_quantification_triggers(self, quantified, unquantified):
        """Identify what statement patterns lead to quantification"""
        print("\nQuantification Triggers:")
        
        # Common number patterns in quantified claims
        number_patterns = []
        for claim in quantified:
            statement = claim.get('statement', '')
            # Find number patterns
            numbers = re.findall(r'\b\d+(?:\.\d+)?(?:\s*(?:million|billion|thousand|%))?', statement.lower())
            number_patterns.extend(numbers)
        
        if number_patterns:
            common_patterns = Counter(number_patterns).most_common(5)
            print("  Common number patterns in quantified claims:")
            for pattern, count in common_patterns:
                print(f"    '{pattern}': {count} times")
        
        # Keywords associated with quantification
        quantified_words = []
        unquantified_words = []
        
        for claim in quantified:
            words = claim.get('statement', '').lower().split()
            quantified_words.extend(words)
        
        for claim in unquantified:
            words = claim.get('statement', '').lower().split()
            unquantified_words.extend(words)
        
        # Find words more common in quantified claims
        quantified_freq = Counter(quantified_words)
        unquantified_freq = Counter(unquantified_words)
        
        distinctive_words = []
        for word in quantified_freq:
            if len(word) > 3 and quantified_freq[word] >= 2:
                q_rate = quantified_freq[word] / len(quantified_words) if len(quantified_words) > 0 else 0
                u_rate = unquantified_freq[word] / len(unquantified_words) if len(unquantified_words) > 0 else 0
                if q_rate > u_rate * 2:  # At least 2x more common in quantified
                    distinctive_words.append((word, q_rate, u_rate))
        
        if distinctive_words:
            print("  Words strongly associated with quantification:")
            for word, q_rate, u_rate in sorted(distinctive_words, key=lambda x: x[1], reverse=True)[:5]:
                print(f"    '{word}': {q_rate:.3f} vs {u_rate:.3f}")
    
    def identify_missed_quantifications(self, unquantified):
        """Identify claims that should have been quantified but weren't"""
        print("\nPotential Missed Quantifications:")
        
        # Look for unquantified claims with obvious numbers
        missed_opportunities = []
        for claim in unquantified:
            statement = claim.get('statement', '')
            # Check for percentage patterns
            if re.search(r'\b\d+(?:\.\d+)?%', statement):
                missed_opportunities.append(('percentage', claim))
            # Check for dollar amounts
            elif re.search(r'\$\d+(?:\.\d+)?(?:\s*(?:million|billion))?', statement):
                missed_opportunities.append(('currency', claim))
            # Check for units
            elif re.search(r'\b\d+(?:\.\d+)?\s*(?:MW|GW|kWh|gallons|tons|trees|people)', statement):
                missed_opportunities.append(('units', claim))
        
        if missed_opportunities:
            print("  Claims with numbers that weren't quantified:")
            for category, claim in missed_opportunities[:5]:  # Show top 5
                statement = claim.get('statement', '')[:100] + "..." if len(claim.get('statement', '')) > 100 else claim.get('statement', '')
                print(f"    [{category}] {claim['source_doc']}: {statement}")
        else:
            print("  No obvious missed quantification opportunities found")
    
    def analyze_aspect_distribution(self):
        """Analyze aspect categorization patterns"""
        print("\n\nASPECT DISTRIBUTION ANALYSIS")
        print("=" * 50)
        
        aspect_counts = Counter(claim.get('aspect', 'unknown') for claim in self.all_claims)
        
        print("Aspect Distribution:")
        for aspect, count in aspect_counts.most_common():
            percentage = count / len(self.all_claims) * 100
            print(f"  {aspect:25} | {count:2d} claims ({percentage:5.1f}%)")
        
        # Check for unexpected aspects
        expected_aspects = ['impact:environmental', 'impact:social', 'impact:financial', 'impact:work']
        unexpected = [aspect for aspect in aspect_counts.keys() if aspect not in expected_aspects]
        
        if unexpected:
            print(f"\nUnexpected Aspects Found:")
            for aspect in unexpected:
                print(f"  {aspect}: {aspect_counts[aspect]} claims")
                # Show example claims for unexpected aspects
                examples = [c for c in self.all_claims if c.get('aspect') == aspect][:2]
                for example in examples:
                    statement = example.get('statement', '')[:60] + "..." if len(example.get('statement', '')) > 60 else example.get('statement', '')
                    print(f"    Example: {statement}")
        
        # Analyze document type vs aspect patterns
        self.analyze_doc_aspect_correlation()
    
    def analyze_doc_aspect_correlation(self):
        """Analyze correlation between document types and aspects"""
        print("\nDocument Type vs Aspect Correlation:")
        
        doc_aspects = defaultdict(lambda: defaultdict(int))
        for claim in self.all_claims:
            doc_type = claim['source_doc']
            aspect = claim.get('aspect', 'unknown')
            doc_aspects[doc_type][aspect] += 1
        
        for doc_type in doc_aspects:
            aspects = doc_aspects[doc_type]
            total = sum(aspects.values())
            print(f"  {doc_type}:")
            for aspect, count in sorted(aspects.items(), key=lambda x: x[1], reverse=True):
                percentage = count / total * 100
                print(f"    {aspect:20} | {count:2d} ({percentage:5.1f}%)")
    
    def identify_extraction_failures(self):
        """Identify potential extraction failures and patterns"""
        print("\n\nEXTRACTION FAILURE ANALYSIS")
        print("=" * 50)
        
        # Documents with unusually low extraction rates
        avg_claims = statistics.mean([len(r['claims']) for r in self.results])
        underperforming = [r for r in self.results if len(r['claims']) < avg_claims * 0.7]
        
        if underperforming:
            print("Underperforming Documents:")
            for result in underperforming:
                efficiency = len(result['claims']) / (result['text_length'] / 100)
                print(f"  {result['document_type']:20} | {len(result['claims'])} claims | {efficiency:.2f} eff")
                print(f"    Possible issues: Low information density, complex language, or prompt mismatch")
        
        # Analyze text characteristics of underperforming docs
        if underperforming:
            self.analyze_underperformance_patterns(underperforming)
    
    def analyze_underperformance_patterns(self, underperforming):
        """Analyze what makes documents underperform"""
        print("\nUnderperformance Pattern Analysis:")
        
        # Compare text characteristics
        high_performing = [r for r in self.results if r not in underperforming]
        
        # Average sentence length
        def avg_sentence_length(text):
            sentences = text.split('.')
            return statistics.mean([len(s.split()) for s in sentences if len(s.strip()) > 0]) if sentences else 0
        
        under_avg_sentence = statistics.mean([avg_sentence_length(self.get_doc_text(r['filename'])) 
                                            for r in underperforming if self.doc_text_available(r['filename'])])
        high_avg_sentence = statistics.mean([avg_sentence_length(self.get_doc_text(r['filename'])) 
                                           for r in high_performing if self.doc_text_available(r['filename'])])
        
        print(f"  Average sentence length:")
        print(f"    Underperforming: {under_avg_sentence:.1f} words")
        print(f"    High performing: {high_avg_sentence:.1f} words")
        
        # Keyword density analysis
        commitment_words = ['committed', 'plan', 'goal', 'target', 'will', 'intend']
        achievement_words = ['achieved', 'completed', 'reduced', 'increased', 'generated', 'saved']
        
        under_commitment_density = self.calculate_keyword_density(underperforming, commitment_words)
        under_achievement_density = self.calculate_keyword_density(underperforming, achievement_words)
        high_commitment_density = self.calculate_keyword_density(high_performing, commitment_words)
        high_achievement_density = self.calculate_keyword_density(high_performing, achievement_words)
        
        print(f"  Keyword density (commitment words):")
        print(f"    Underperforming: {under_commitment_density:.3f}")
        print(f"    High performing: {high_commitment_density:.3f}")
        print(f"  Keyword density (achievement words):")
        print(f"    Underperforming: {under_achievement_density:.3f}")
        print(f"    High performing: {high_achievement_density:.3f}")
    
    def doc_text_available(self, filename):
        """Check if we can access the original document text"""
        import os
        return os.path.exists(filename)
    
    def get_doc_text(self, filename):
        """Get original document text for analysis"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
    
    def calculate_keyword_density(self, results, keywords):
        """Calculate keyword density for a set of documents"""
        total_words = 0
        keyword_count = 0
        
        for result in results:
            if self.doc_text_available(result['filename']):
                text = self.get_doc_text(result['filename']).lower()
                words = text.split()
                total_words += len(words)
                keyword_count += sum(1 for word in words if any(kw in word for kw in keywords))
        
        return keyword_count / total_words if total_words > 0 else 0
    
    def generate_optimization_recommendations(self):
        """Generate specific recommendations for system improvement"""
        print("\n\nOPTIMIZATION RECOMMENDATIONS")
        print("=" * 50)
        
        recommendations = []
        
        # Based on confidence analysis
        low_conf_aspects = []
        aspect_confidences = defaultdict(list)
        for claim in self.all_claims:
            aspect_confidences[claim.get('aspect', 'unknown')].append(claim.get('confidence', 0))
        
        for aspect, confidences in aspect_confidences.items():
            if statistics.mean(confidences) < 0.85:
                low_conf_aspects.append(aspect)
        
        if low_conf_aspects:
            recommendations.append(f"Improve prompt specificity for aspects: {', '.join(low_conf_aspects)}")
        
        # Based on quantification analysis
        underperforming_docs = [r for r in self.results if r['quantified_claims'] / len(r['claims']) < 0.5 if len(r['claims']) > 0]
        if underperforming_docs:
            doc_types = [r['document_type'] for r in underperforming_docs]
            recommendations.append(f"Add quantification examples for document types: {', '.join(doc_types)}")
        
        # Based on aspect distribution
        aspect_counts = Counter(claim.get('aspect', 'unknown') for claim in self.all_claims)
        if aspect_counts['impact:environmental'] > sum(aspect_counts.values()) * 0.5:
            recommendations.append("Prompt may be biased toward environmental content - test with more diverse domains")
        
        # Based on extraction efficiency
        low_efficiency = [r for r in self.results if len(r['claims']) / (r['text_length'] / 100) < 0.6]
        if low_efficiency:
            recommendations.append("Some document types have low extraction efficiency - consider prompt optimization")
        
        print("Priority Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        if not recommendations:
            print("  System performing well across all analyzed dimensions")
        
        # Specific prompt improvements
        print("\nSpecific Prompt Improvement Suggestions:")
        print("  1. Add examples of commitment vs. achievement language")
        print("  2. Include more diverse aspect categories in training examples")
        print("  3. Strengthen number extraction patterns for edge cases")
        print("  4. Consider document-type-specific prompt variations")

def main():
    """Main function to run extraction analysis"""
    # Find the most recent results file
    results_files = glob.glob("extraction_test_results_*.json")
    if not results_files:
        print("No extraction results files found. Run test_different_documents.py first.")
        return
    
    latest_file = max(results_files)
    print(f"Analyzing results from: {latest_file}")
    print("=" * 60)
    
    analyzer = ExtractionAnalyzer(latest_file)
    
    analyzer.analyze_confidence_patterns()
    analyzer.analyze_quantification_patterns()
    analyzer.analyze_aspect_distribution()
    analyzer.identify_extraction_failures()
    analyzer.generate_optimization_recommendations()
    
    print("\n" + "=" * 60)
    print("Analysis complete. Use insights to optimize extraction system.")

if __name__ == "__main__":
    main()