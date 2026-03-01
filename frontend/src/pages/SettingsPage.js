import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  CssBaseline,
  Typography,
  Paper,
  TextField,
  Button,
  Alert,
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Link,
} from '@mui/material';
import { ArrowBack as ArrowBackIcon, Save as SaveIcon, Science as TestIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';

const SettingsPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  const [settings, setSettings] = useState({
    api_key: '',
    model: 'gemini-2.5-flash-lite',
    has_api_key: false,
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getSettings();
      setAvailableModels(data.available_models || []);
      if (data.settings) {
        setSettings({
          api_key: '', // Не загружаем ключ для безопасности
          model: data.settings.model || 'gemini-2.5-flash-lite',
          has_api_key: data.settings.has_api_key,
        });
      }
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTestApiKey = async () => {
    if (!settings.api_key) {
      setError('Введите API ключ для проверки');
      return;
    }

    try {
      setTesting(true);
      setError('');
      await apiClient.testApiKey(settings.api_key);
      setSuccess('API ключ действителен!');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(`Ошибка API ключа: ${err.message}`);
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      
      const updateData = {
        model: settings.model,
      };
      
      // Отправляем API ключ только если он был изменён
      if (settings.api_key) {
        updateData.api_key = settings.api_key;
      }
      
      await apiClient.updateSettings(updateData);
      setSuccess('Настройки сохранены!');
      setSettings({ ...settings, api_key: '' }); // Очищаем поле ключа
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setSettings({ ...settings, [field]: value });
    if (error) setError('');
    if (success) setSuccess('');
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <CssBaseline />

      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/chats')}
            sx={{ mr: 2 }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Настройки
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Настройки Gemini API
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
              {success}
            </Alert>
          )}

          <Box sx={{ mb: 4 }}>
            <Typography variant="body2" color="text.secondary" paragraph>
              Здесь вы можете указать свой API ключ Google Gemini и выбрать модель.
              Если не указать ключ, будет использоваться серверный ключ.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Получить API ключ можно на{' '}
              <Link
                href="https://aistudio.google.com/apikey"
                target="_blank"
                rel="noopener noreferrer"
              >
                Google AI Studio
              </Link>
            </Typography>
          </Box>

          <TextField
            fullWidth
            label="API ключ Google"
            type="password"
            value={settings.api_key}
            onChange={(e) => handleChange('api_key', e.target.value)}
            placeholder="AIzaSy..."
            helperText={
              settings.has_api_key && !settings.api_key
                ? 'У вас уже сохранён API ключ. Введите новый, чтобы заменить его, или оставьте пустым.'
                : 'Введите ваш персональный API ключ'
            }
            sx={{ mb: 3 }}
          />

          <Button
            variant="outlined"
            startIcon={testing ? <CircularProgress size={20} /> : <TestIcon />}
            onClick={handleTestApiKey}
            disabled={!settings.api_key || testing}
            sx={{ mb: 4 }}
          >
            {testing ? 'Проверка...' : 'Проверить API ключ'}
          </Button>

          <FormControl fullWidth sx={{ mb: 4 }}>
            <InputLabel>Модель Gemini</InputLabel>
            <Select
              value={settings.model}
              label="Модель Gemini"
              onChange={(e) => handleChange('model', e.target.value)}
            >
              {availableModels.length > 0 ? (
                availableModels.map((model) => (
                  <MenuItem key={model} value={model}>
                    {model}
                  </MenuItem>
                ))
              ) : (
                <>
                  <MenuItem value="gemini-2.5-flash-lite">gemini-2.5-flash-lite</MenuItem>
                  <MenuItem value="gemini-2.5-flash">gemini-2.5-flash</MenuItem>
                  <MenuItem value="gemini-3-flash-preview">gemini-3-flash-preview</MenuItem>
                </>
              )}
            </Select>
            <FormHelperText>
              Выберите модель для генерации ответов
            </FormHelperText>
          </FormControl>

          <Button
            variant="contained"
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSave}
            disabled={saving}
            size="large"
          >
            {saving ? 'Сохранение...' : 'Сохранить настройки'}
          </Button>
        </Paper>
      </Container>
    </Box>
  );
};

export default SettingsPage;
