import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  CssBaseline,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  AppBar,
  Toolbar,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Chat as ChatIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import ThemeToggle from '../components/ThemeToggle';
import apiClient from '../api/client';

const ChatList = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newChatTitle, setNewChatTitle] = useState('');
  const [deletingChatId, setDeletingChatId] = useState(null);

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getChats();
      setChats(data);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChat = async () => {
    if (!newChatTitle.trim()) return;

    try {
      const newChat = await apiClient.createChat(newChatTitle);
      setChats([newChat, ...chats]);
      setNewChatTitle('');
      setDialogOpen(false);
      navigate(`/chat/${newChat.id}`);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteChat = async (chatId) => {
    try {
      await apiClient.deleteChat(chatId);
      setChats(chats.filter((chat) => chat.id !== chatId));
      setDeletingChatId(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <CssBaseline />
      
      <AppBar position="static">
        <Toolbar>
          <ChatIcon sx={{ mr: 2 }} />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            FastAPI Gemini Clone
          </Typography>
          <Typography variant="body2" sx={{ mr: 2 }}>
            {user?.email}
          </Typography>
          <ThemeToggle />
          <IconButton color="inherit" onClick={handleLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 3, minHeight: '80vh' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" component="h1">
              Мои чаты
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setDialogOpen(true)}
            >
              Новый чат
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : chats.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <ChatIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                У вас пока нет чатов
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Создайте первый чат, чтобы начать общение с AI
              </Typography>
            </Box>
          ) : (
            <List>
              {chats.map((chat) => (
                <ListItem
                  key={chat.id}
                  button
                  onClick={() => navigate(`/chat/${chat.id}`)}
                  sx={{
                    borderRadius: 2,
                    mb: 1,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <ChatIcon sx={{ mr: 2, color: 'primary.main' }} />
                  <ListItemText
                    primary={chat.title}
                    secondary={new Date(chat.created_at).toLocaleDateString('ru-RU', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      color="error"
                      onClick={(e) => {
                        e.stopPropagation();
                        setDeletingChatId(chat.id);
                      }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          )}
        </Paper>
      </Container>

      {/* Dialog создания нового чата */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Создать новый чат</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Название чата"
            fullWidth
            value={newChatTitle}
            onChange={(e) => setNewChatTitle(e.target.value)}
            placeholder="Например: Помощь с кодом"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Отмена</Button>
          <Button onClick={handleCreateChat} variant="contained" disabled={!newChatTitle.trim()}>
            Создать
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog подтверждения удаления */}
      <Dialog open={!!deletingChatId} onClose={() => setDeletingChatId(null)}>
        <DialogTitle>Удалить чат?</DialogTitle>
        <DialogContent>
          <Typography>
            Вы уверены, что хотите удалить этот чат? Это действие нельзя отменить.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeletingChatId(null)}>Отмена</Button>
          <Button
            onClick={() => handleDeleteChat(deletingChatId)}
            variant="contained"
            color="error"
          >
            Удалить
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatList;
