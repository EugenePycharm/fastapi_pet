import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Container,
  CssBaseline,
  Typography,
  Paper,
  TextField,
  IconButton,
  AppBar,
  Toolbar,
  Alert,
  CircularProgress,
  Avatar,
  Fab,
  Zoom,
} from '@mui/material';
import {
  Send as SendIcon,
  ArrowBack as ArrowBackIcon,
  SmartToy as SmartToyIcon,
  Person as PersonIcon,
  KeyboardArrowDown as ArrowDownIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import MarkdownRenderer from '../components/MarkdownRenderer';
import ThemeToggle from '../components/ThemeToggle';

const Chat = () => {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const [chat, setChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [streamingMessage, setStreamingMessage] = useState('');
  const [showScrollButton, setShowScrollButton] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const loadChat = useCallback(async () => {
    try {
      setLoading(true);
      const data = await apiClient.getChat(chatId);
      setChat(data);
      setMessages(data.messages || []);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [chatId]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    loadChat();
  }, [loadChat]);

  // Скролл вниз только при новых сообщениях
  useEffect(() => {
    if (messages.length > 0 || streamingMessage) {
      scrollToBottom();
    }
  }, [messages.length, streamingMessage]);

  // Отслеживание прокрутки для кнопки "Вниз"
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight;
      const clientHeight = document.documentElement.clientHeight;
      // Показываем кнопку если прокрутили больше 300px от низа
      const scrolledFromBottom = scrollHeight - scrollTop - clientHeight;
      setShowScrollButton(scrolledFromBottom > 300);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim() || sending) return;

    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setSending(true);
    setStreamingMessage('');

    try {
      let assistantContent = '';
      await apiClient.sendMessageStream(
        chatId,
        userMessage.content,
        'user',
        (chunk, timestamp) => {
          assistantContent += chunk;
          setStreamingMessage(assistantContent);
        }
      );

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: assistantContent,
        created_at: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);
      setStreamingMessage('');
      await loadChat();
    } catch (err) {
      setError(err.message);
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  }, [inputValue, sending, chatId, loadChat]);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  const renderMessage = useCallback((message, index) => {
    const isUser = message.role === 'user';
    const isStreaming = index === messages.length - 1 && streamingMessage && !isUser;
    const messageContent = isStreaming ? streamingMessage : message.content;

    return (
      <Box
        key={message.id || index}
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
          width: '100%',
        }}
      >
        {!isUser && (
          <Avatar sx={{ mr: 1, bgcolor: 'primary.main', flexShrink: 0 }}>
            <SmartToyIcon />
          </Avatar>
        )}
        <Paper
          elevation={1}
          sx={{
            p: 2,
            maxWidth: 'calc(100% - 60px)',
            minWidth: 0,
            borderRadius: 2,
            backgroundColor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary',
            wordBreak: 'break-word',
            overflowWrap: 'break-word',
            '& .markdown-body': {
              color: isUser ? 'inherit' : 'text.primary',
              maxWidth: '100%',
              '& p': {
                wordBreak: 'break-word',
                overflowWrap: 'break-word',
              },
            },
            '& pre': {
              backgroundColor: isUser ? 'rgba(255,255,255,0.1)' : 'transparent',
              maxWidth: '100%',
              overflowX: 'auto',
            },
            '& code': {
              backgroundColor: isUser ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.06)',
              color: isUser ? 'inherit' : '#e83e8c',
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
            },
          }}
        >
          {isUser ? (
            <Typography
              variant="body1"
              sx={{
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                overflowWrap: 'break-word',
                maxWidth: '100%',
              }}
            >
              {messageContent}
            </Typography>
          ) : (
            <MarkdownRenderer content={messageContent} />
          )}
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              mt: 1,
              color: isUser ? 'primary.light' : 'text.secondary',
              wordBreak: 'break-word',
            }}
          >
            {new Date(message.created_at).toLocaleTimeString('ru-RU', {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Typography>
        </Paper>
        {isUser && (
          <Avatar sx={{ ml: 1, bgcolor: 'secondary.main' }}>
            <PersonIcon />
          </Avatar>
        )}
      </Box>
    );
  }, [streamingMessage, messages.length]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <CssBaseline />

      {/* Fixed AppBar - закреплён вверху */}
      <AppBar position="fixed" sx={{ top: 0, zIndex: 1200 }}>
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
            {chat?.title || 'Чат'}
          </Typography>
          <ThemeToggle />
          <Avatar sx={{ bgcolor: 'secondary.main' }}>
            <PersonIcon />
          </Avatar>
        </Toolbar>
      </AppBar>

      {/* Spacer для AppBar */}
      <Toolbar />

      <Container maxWidth="lg" sx={{ mt: 2, mb: 2, flexGrow: 1 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Блок с сообщениями - без прокрутки, часть страницы */}
        <Paper
          elevation={3}
          sx={{
            p: 3,
            mb: 2,
          }}
        >
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
              <CircularProgress />
            </Box>
          ) : messages.length === 0 ? (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                py: 8,
                textAlign: 'center',
              }}
            >
              <SmartToyIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Начните разговор
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Задайте вопрос или начните обсуждение темы
              </Typography>
            </Box>
          ) : (
            <>
              <Box>
                {messages.map((message, index) => renderMessage(message, index))}
                {streamingMessage && (
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'flex-start',
                      mb: 2,
                    }}
                  >
                    <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                      <SmartToyIcon />
                    </Avatar>
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        maxWidth: '70%',
                        borderRadius: 2,
                        backgroundColor: 'background.paper',
                      }}
                    >
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {streamingMessage}
                        <span style={{ display: 'inline-block', animation: 'blink 1s infinite' }}>▊</span>
                      </Typography>
                    </Paper>
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </Box>
            </>
          )}
        </Paper>

        {/* Spacer для фиксированного поля ввода */}
        <Box sx={{ height: 100 }} />
      </Container>

      {/* Fixed поле ввода - закреплено внизу */}
      <Paper
        elevation={3}
        sx={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          p: 2,
          zIndex: 1100,
          backgroundColor: 'background.paper',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              ref={inputRef}
              fullWidth
              multiline
              maxRows={6}
              placeholder="Введите сообщение..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={sending}
              variant="outlined"
              sx={{ '& .MuiInputBase-root': { backgroundColor: 'background.paper' } }}
            />
            <IconButton
              color="primary"
              variant="contained"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || sending}
              sx={{ minWidth: 56 }}
            >
              {sending ? <CircularProgress size={24} /> : <SendIcon />}
            </IconButton>
          </Box>
        </Container>
      </Paper>

      {/* Кнопка "Вниз" */}
      <Zoom in={showScrollButton}>
        <Fab
          color="primary"
          size="medium"
          onClick={scrollToBottom}
          sx={{
            position: 'fixed',
            bottom: 100,
            right: 24,
            zIndex: 1201,
            boxShadow: 3,
          }}
        >
          <ArrowDownIcon />
        </Fab>
      </Zoom>

      <style>
        {`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }
        `}
      </style>
    </Box>
  );
};

export default Chat;
