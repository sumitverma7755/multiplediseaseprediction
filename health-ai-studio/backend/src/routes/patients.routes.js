import { Router } from 'express';
import { addPatient, listPatientReports, listPatients } from '../controllers/patients.controller.js';

const router = Router();

router.get('/', listPatients);
router.post('/', addPatient);
router.get('/:patientId/reports', listPatientReports);

export default router;
