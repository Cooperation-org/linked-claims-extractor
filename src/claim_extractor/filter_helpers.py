"""
Helper functions for claims filtering.
These functions help identify verifiable vs non-verifiable claims.
"""

def has_future_tense(claim_text):
	"""
	Check if claim contains future tense words that indicate plans rather than completed actions.

	Args:
		claim_text (str): The claim to check

	Returns:
		bool: True if future tense found, False otherwise

	Examples:
		>>> has_future_tense("We will serve 1000 people")
		True
		>>> has_future_tense("We served 1000 people")
		False
	"""
	future_indicators = [
		'will',
		'plans to',
		'planning to',
		'going to',
		'intends to',
		'aims to',
		'hopes to',
		'expects to'
	]

	# Convert to lowercase for case-insensitive matching
	text_lower = claim_text.lower()

	# Check each future indicator
	for indicator in future_indicators:
		if indicator in text_lower:
			return True

	# If no future indicators found, return False
	return False

def extract_numbers(claim_text):
	"""
	Extract all numbers from a claim text.

	Numbers suggest measurable, verifiable outcomes.

	Args:
		claim_text (str): The claim to analyze

	Returns:
		list: List of number strings found in text

	Examples:
		>>> extract_numbers("We served 1000 people and built 50 wells")
		['1000', '50']
		>>> extract_numbers("We believe in clean water")
		[]
	"""
	import re

	# Find all sequences of digits
	numbers = re.findall(r'\d+', claim_text)

	return numbers


# TEST YOUR FUNCTIONS
if __name__ == "__main__":
	# Test cases
	test_claims = [
		"We served 1000 people in 2024",
		"We will expand to 5 countries next year",
		"Built 50 wells in rural communities",
		"Plans to serve 10,000 more families",
		"Our organization provided clean water to 45,000 people"
	]

	print("Testing Future Tense Detection:")
	print("=" * 50)

	for claim in test_claims:
		result = has_future_tense(claim)
		status = "X FUTURE (filter out)" if result else "✓ PAST (keep)"
		print(f"{status}: {claim}")

	# NEW TEST: Number extraction
	print("\n\nTesting Number Extraction:")
	print("=" * 50)

	for claim in test_claims:
		numbers = extract_numbers(claim)
		if numbers:
			print(f"Found {numbers}: {claim}")
		else:
			print(f"No numbers: {claim}")

	# COMBINED TEST: Which claims are verifiable?
	print("\n\nVerifiability Analysis:")
	print("=" * 50)

	for claim in test_claims:
		has_future = has_future_tense(claim)
		has_numbers = len(extract_numbers(claim)) > 0

		is_verifiable = not has_future and has_numbers

		if is_verifiable:
			print(f"✓ VERIFIABLE: {claim}")
		else:
			reasons = []
			if has_future:
				reasons.append("future tense")
			if not has_numbers:
				reasons.append("no metrics")
			print(f"X NOT VERIFIABLE ({', '.join(reasons)}): {claim}")