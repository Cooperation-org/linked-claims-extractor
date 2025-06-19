# Impact Verification Demo

## Quick Start

```bash
# Install dependencies
npm install

# Start the development server
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## Demo Features

### For Organizations
1. **Upload Report** - Drag & drop annual report PDF
2. **Review Claims** - See extracted verifiable claims with beneficiary details
3. **Send Validation Links** - Generate unique links for beneficiaries
4. **Track Validations** - Real-time dashboard showing validation progress
5. **Trust Score** - Build public trust profile based on human validations

### For Beneficiaries
- **Simple Validation** - Click link, no login required
- **Three Options** - Yes / No / Partially true
- **Add Testimonial** - Optional comment field
- **Mobile Friendly** - Works on any device

## Key Screens

1. **Home** - Value proposition and how it works
2. **Upload** - PDF upload interface
3. **Review** - Extracted claims with beneficiary targeting
4. **Tracking** - Live validation feed and progress
5. **Beneficiary View** - Simple validation interface

## The Story

This demo shows how organizations can:
- Transform static PDF reports into living, verified trust
- Connect directly with the people they've helped
- Build credibility through human verification, not technology

The focus is on **real people verifying real impact**.

## Demo Flow

1. Organization uploads their 2023 annual report
2. System extracts 3 sample claims:
   - Food bank: 15,000 meals to 500 families
   - Healthcare: Trained 85 workers in Nigeria
   - Water: 12 wells serving 3,000 people
3. Organization sends validation links via SMS/WhatsApp
4. Beneficiaries click and validate with comments
5. Real-time dashboard shows growing trust score

## Next Steps

To connect this demo to the real backend:
1. Wire up PDF upload to extractor service
2. Connect validation links to backend API
3. Store validations in trust claim database
4. Generate real validation tokens
5. Build public trust profiles
