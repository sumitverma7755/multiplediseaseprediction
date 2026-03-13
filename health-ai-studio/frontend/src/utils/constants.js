export const DISEASE_MODULES = [
  {
    key: 'diabetes',
    title: 'Diabetes Risk Prediction',
    description: 'Screen glucose metabolism risk using clinical and lifestyle indicators.',
    statLabel: 'Metabolic risk model',
    color: 'from-cyan-500 to-teal-600'
  },
  {
    key: 'heart',
    title: 'Heart Disease Prediction',
    description: 'Estimate cardiovascular risk with symptom, ECG, and lipid profile features.',
    statLabel: 'Cardio risk model',
    color: 'from-rose-500 to-red-600'
  },
  {
    key: 'parkinsons',
    title: "Parkinson's Prediction",
    description: 'Evaluate neuro-motor voice biomarkers for early Parkinson risk.',
    statLabel: 'Neuro voice model',
    color: 'from-violet-500 to-indigo-600'
  }
];

export const NAV_ITEMS = [
  { label: 'Dashboard', path: '/' },
  { label: 'Patients', path: '/patients' },
  { label: 'History', path: '/history' }
];

export const SCREENING_INPUTS = {
  diabetes: [
    { id: 'pregnancies', label: 'Pregnancies', type: 'number', min: 0, max: 20, step: 1, defaultValue: 1 },
    { id: 'glucose', label: 'Glucose (mg/dL)', type: 'number', min: 50, max: 300, step: 1, defaultValue: 120 },
    { id: 'bloodPressure', label: 'Blood Pressure (mm Hg)', type: 'number', min: 40, max: 160, step: 1, defaultValue: 80 },
    { id: 'bmi', label: 'BMI', type: 'number', min: 10, max: 55, step: 0.1, defaultValue: 26.5 },
    { id: 'age', label: 'Age', type: 'number', min: 18, max: 100, step: 1, defaultValue: 35 }
  ],
  heart: [
    { id: 'age', label: 'Age', type: 'number', min: 18, max: 100, step: 1, defaultValue: 52 },
    { id: 'cholesterol', label: 'Cholesterol (mg/dL)', type: 'number', min: 80, max: 500, step: 1, defaultValue: 210 },
    { id: 'restingBP', label: 'Resting Blood Pressure', type: 'number', min: 70, max: 220, step: 1, defaultValue: 130 },
    { id: 'maxHeartRate', label: 'Max Heart Rate', type: 'number', min: 60, max: 220, step: 1, defaultValue: 150 },
    { id: 'exerciseAngina', label: 'Exercise Angina (0/1)', type: 'number', min: 0, max: 1, step: 1, defaultValue: 0 }
  ],
  parkinsons: [
    { id: 'jitter', label: 'Jitter', type: 'number', min: 0, max: 1, step: 0.001, defaultValue: 0.02 },
    { id: 'shimmer', label: 'Shimmer', type: 'number', min: 0, max: 1, step: 0.001, defaultValue: 0.04 },
    { id: 'hnr', label: 'HNR', type: 'number', min: 0, max: 40, step: 0.1, defaultValue: 22.5 },
    { id: 'rpde', label: 'RPDE', type: 'number', min: 0, max: 1, step: 0.01, defaultValue: 0.41 },
    { id: 'ppe', label: 'PPE', type: 'number', min: 0, max: 1, step: 0.01, defaultValue: 0.21 }
  ]
};
