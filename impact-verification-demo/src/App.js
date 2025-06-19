import React, { useState } from 'react';
import { Upload, Users, CheckCircle, MessageCircle, Send, Globe, Heart, ArrowRight, FileText, UserCheck, MapPin, Calendar } from 'lucide-react';

const App = () => {
  const [currentView, setCurrentView] = useState('home');
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [showValidation, setShowValidation] = useState(false);

  // Demo data
  const extractedClaims = [
    {
      id: 1,
      claim: "provided_meals_to",
      statement: "Provided 15,000 meals to 500 families in Phoenix, Arizona",
      location: "Phoenix, Arizona",
      beneficiaryCount: 500,
      beneficiaryType: "families",
      amount: "15,000 meals",
      date: "January - December 2023",
      validationTarget: 100,
      validated: 0
    },
    {
      id: 2,
      claim: "trained",
      statement: "Trained 85 healthcare workers in maternal health practices in rural Nigeria",
      location: "Rural Nigeria",
      beneficiaryCount: 85,
      beneficiaryType: "healthcare workers",
      amount: "85 professionals",
      date: "March - November 2023",
      validationTarget: 50,
      validated: 0
    },
    {
      id: 3,
      claim: "funded_water_wells",
      statement: "Funded construction of 12 water wells serving 3,000 people in Kenya",
      location: "Turkana County, Kenya",
      beneficiaryCount: 3000,
      beneficiaryType: "community members",
      amount: "12 water wells",
      date: "2023",
      validationTarget: 12,
      validated: 0
    }
  ];

  const validationResponses = [
    { name: "Maria Garcia", response: "Yes", comment: "The meals really helped our family through a difficult time. Thank you!", location: "Phoenix" },
    { name: "Dr. Adebayo", response: "Yes", comment: "The training was excellent and has improved our clinic's maternal care significantly.", location: "Lagos, Nigeria" },
    { name: "John Lokuruka", response: "Yes", comment: "Our village now has clean water for the first time. Children are healthier!", location: "Turkana, Kenya" }
  ];

  const BeneficiaryValidationView = () => {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-xl shadow-lg p-6">
            {/* Header */}
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <UserCheck className="h-8 w-8 text-blue-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900">Validation Request</h2>
              <p className="text-sm text-gray-600 mt-1">Your response helps build trust</p>
            </div>

            {/* Organization Info */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-600 mb-2">Hope Foundation asks:</p>
              <p className="font-medium text-gray-900">
                "Did we provide meals to families in your community during 2023?"
              </p>
            </div>

            {/* Validation Buttons */}
            <div className="space-y-3 mb-6">
              <button className="w-full py-3 px-4 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg flex items-center justify-center space-x-2 transition-colors">
                <CheckCircle className="h-5 w-5" />
                <span>Yes, this is true</span>
              </button>
              
              <button className="w-full py-3 px-4 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg flex items-center justify-center space-x-2 transition-colors">
                <span>No, this didn't happen</span>
              </button>
              
              <button className="w-full py-3 px-4 bg-yellow-600 hover:bg-yellow-700 text-white font-medium rounded-lg flex items-center justify-center space-x-2 transition-colors">
                <span>Partially true</span>
              </button>
            </div>

            {/* Optional Comment */}
            <div className="border-t pt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Add a comment (optional)
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                rows="3"
                placeholder="Share your experience..."
              />
              <button className="mt-3 w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors">
                Submit Validation
              </button>
            </div>

            {/* Privacy Note */}
            <p className="text-xs text-gray-500 text-center mt-4">
              Your response is anonymous and helps verify real impact
            </p>
          </div>
        </div>
      </div>
    );
  };

  if (showValidation) {
    return <BeneficiaryValidationView />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Users className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">LinkedClaims</h1>
                <p className="text-sm text-gray-600">Human-Verified Impact</p>
              </div>
            </div>
            <button
              onClick={() => setShowValidation(true)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View as Beneficiary →
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      {currentView === 'home' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Your impact, verified by the people you've impacted
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Transform your annual report into trusted, human-verified claims. 
              Let your beneficiaries confirm your impact directly.
            </p>
          </div>

          {/* How it Works */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">How It Works</h3>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                  <Upload className="h-8 w-8 text-blue-600" />
                </div>
                <h4 className="font-semibold text-lg mb-2">1. Upload Report</h4>
                <p className="text-gray-600">Upload your annual report and we'll extract specific, verifiable claims</p>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                  <Send className="h-8 w-8 text-green-600" />
                </div>
                <h4 className="font-semibold text-lg mb-2">2. Send to Beneficiaries</h4>
                <p className="text-gray-600">Send validation links directly to the people you've helped</p>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-100 rounded-full mb-4">
                  <Heart className="h-8 w-8 text-purple-600" />
                </div>
                <h4 className="font-semibold text-lg mb-2">3. Build Real Trust</h4>
                <p className="text-gray-600">Receive validations and testimonials from real people</p>
              </div>
            </div>
            
            <div className="text-center mt-8">
              <button
                onClick={() => setCurrentView('upload')}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg inline-flex items-center space-x-2 transition-colors"
              >
                <span>Start Demo</span>
                <ArrowRight className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Trust Stats */}
          <div className="grid md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-blue-600">2,847</div>
              <div className="text-sm text-gray-600">Human Validations</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-green-600">89%</div>
              <div className="text-sm text-gray-600">Validation Rate</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-purple-600">47</div>
              <div className="text-sm text-gray-600">Organizations</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="text-3xl font-bold text-orange-600">15</div>
              <div className="text-sm text-gray-600">Countries</div>
            </div>
          </div>
        </div>
      )}

      {/* Upload View */}
      {currentView === 'upload' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-8">
              <FileText className="h-16 w-16 text-blue-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Annual Report</h2>
              <p className="text-gray-600">We'll extract verifiable claims that can be validated by real people</p>
            </div>
            
            <div className="max-w-xl mx-auto">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <button
                  onClick={() => setCurrentView('review')}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg inline-flex items-center space-x-2 transition-colors"
                >
                  <Upload className="h-5 w-5" />
                  <span>Select PDF File</span>
                </button>
                <p className="text-sm text-gray-500 mt-4">or drag and drop your file here</p>
              </div>
              
              <div className="mt-6 bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  <strong>Pro tip:</strong> Claims work best when they include specific numbers, 
                  locations, and timeframes that beneficiaries can verify.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Review Claims View */}
      {currentView === 'review' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Review Extracted Claims</h2>
              <p className="text-gray-600">Select claims to send for human verification</p>
            </div>

            <div className="space-y-4 mb-8">
              {extractedClaims.map((claim) => (
                <div
                  key={claim.id}
                  className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 cursor-pointer transition-colors"
                  onClick={() => setSelectedClaim(claim)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-grow">
                      <p className="font-medium text-gray-900 mb-2">{claim.statement}</p>
                      <div className="flex flex-wrap gap-2 mb-3">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          <MapPin className="h-3 w-3 mr-1" />
                          {claim.location}
                        </span>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <Users className="h-3 w-3 mr-1" />
                          {claim.beneficiaryCount} {claim.beneficiaryType}
                        </span>
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          <Calendar className="h-3 w-3 mr-1" />
                          {claim.date}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        Target validations: <strong>{claim.validationTarget}</strong> beneficiaries
                      </div>
                    </div>
                    <button className="ml-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg text-sm transition-colors">
                      Send for Validation
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-between items-center">
              <button
                onClick={() => setCurrentView('upload')}
                className="text-gray-600 hover:text-gray-800 font-medium"
              >
                ← Back
              </button>
              <button
                onClick={() => setCurrentView('tracking')}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg inline-flex items-center space-x-2 transition-colors"
              >
                <span>Continue to Validation</span>
                <ArrowRight className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Validation Tracking View */}
      {currentView === 'tracking' && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Real-Time Validation Tracking</h2>
            
            {/* Live validation feed */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Validations</h3>
              <div className="space-y-3">
                {validationResponses.map((response, idx) => (
                  <div key={idx} className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="flex items-center space-x-2 mb-1">
                          <CheckCircle className="h-5 w-5 text-green-600" />
                          <span className="font-medium text-gray-900">{response.name}</span>
                          <span className="text-sm text-gray-500">• {response.location}</span>
                        </div>
                        <p className="text-sm text-gray-700 italic">"{response.comment}"</p>
                      </div>
                      <span className="text-sm text-gray-500">2 mins ago</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Progress bars */}
            <div className="space-y-6">
              {extractedClaims.map((claim) => (
                <div key={claim.id} className="border border-gray-200 rounded-lg p-4">
                  <p className="font-medium text-gray-900 mb-3">{claim.statement}</p>
                  <div className="mb-2">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Validation Progress</span>
                      <span>47 of {claim.validationTarget} ({Math.round(47/claim.validationTarget * 100)}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{width: '47%'}}></div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-4 text-gray-600">
                      <span className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-600 mr-1" />
                        45 Yes
                      </span>
                      <span className="flex items-center">
                        <MessageCircle className="h-4 w-4 text-yellow-600 mr-1" />
                        2 Partial
                      </span>
                    </div>
                    <button className="text-blue-600 hover:text-blue-700 font-medium">
                      View Details →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Trust Score Card */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">Your Trust Score</h3>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-5xl font-bold mb-2">89%</div>
                <p className="text-blue-100">Based on 147 human validations</p>
              </div>
              <div className="text-right">
                <button className="bg-white text-blue-600 font-medium py-2 px-4 rounded-lg hover:bg-blue-50 transition-colors">
                  View Public Profile
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
