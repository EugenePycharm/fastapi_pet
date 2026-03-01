import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  CssBaseline,
  Link,
  TextField,
  Typography,
  Alert,
  Paper,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const steps = ['Регистрация', 'Готово'];

const RegisterForm = () => {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [validationError, setValidationError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    if (error) clearError();
    if (validationError) setValidationError('');
  };

  const validateForm = () => {
    if (formData.password.length < 8) {
      setValidationError('Пароль должен содержать минимум 8 символов');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setValidationError('Пароли не совпадают');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    const success = await register(formData.email, formData.password);
    setLoading(false);

    if (success) {
      setActiveStep(1);
      setTimeout(() => {
        navigate('/chats');
      }, 1500);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {activeStep === 0 && (
            <>
              <Typography component="h1" variant="h5" align="center" gutterBottom>
                Регистрация
              </Typography>
              
              {(error || validationError) && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error || validationError}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  label="Email"
                  name="email"
                  autoComplete="email"
                  autoFocus
                  value={formData.email}
                  onChange={handleChange}
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Пароль"
                  type="password"
                  id="password"
                  autoComplete="new-password"
                  value={formData.password}
                  onChange={handleChange}
                  helperText="Минимум 8 символов"
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="confirmPassword"
                  label="Подтвердите пароль"
                  type="password"
                  id="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ mt: 3, mb: 2 }}
                >
                  {loading ? 'Регистрация...' : 'Зарегистрироваться'}
                </Button>
                
                <Typography align="center">
                  Уже есть аккаунт?{' '}
                  <Link component={RouterLink} to="/login" underline="hover">
                    Войти
                  </Link>
                </Typography>
              </Box>
            </>
          )}

          {activeStep === 1 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" gutterBottom>
                Регистрация успешна!
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Перенаправление...
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default RegisterForm;
