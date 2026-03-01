import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Box, Paper, Typography, useTheme } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import IconButton from '@mui/material/IconButton';

const MarkdownRenderer = ({ content }) => {
  const [copiedCode, setCopiedCode] = React.useState(null);
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const copyToClipboard = async (code, index) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(index);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <ReactMarkdown
      children={content}
      components={{
        // Инлайн код
        code({ node, inline, className, children, ...props }) {
          if (inline) {
            return (
              <Box
                component="span"
                sx={{
                  backgroundColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.06)',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  fontFamily: '"Fira Code", "Consolas", "Monaco", monospace',
                  fontSize: '0.9em',
                  color: isDark ? '#f48771' : '#e83e8c',
                }}
              >
                {children}
              </Box>
            );
          }

          // Блок кода
          const match = /language-(\w+)/.exec(className || '');
          const language = match ? match[1] : 'text';
          const code = String(children).replace(/\n$/, '');
          const codeIndex = props['data-code-index'] || 0;

          return (
            <Paper
              elevation={2}
              sx={{
                my: 2,
                overflow: 'hidden',
                borderRadius: 2,
              }}
            >
              {/* Заголовок с языком и кнопкой копирования */}
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '8px 16px',
                  backgroundColor: isDark ? '#2d2d2d' : '#f6f8fa',
                  borderBottom: isDark ? '1px solid #404040' : '1px solid #e1e4e8',
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: isDark ? '#abb2bf' : '#24292e',
                    fontFamily: 'monospace',
                    fontWeight: 'bold',
                  }}
                >
                  {language.toUpperCase()}
                </Typography>
                <IconButton
                  size="small"
                  onClick={() => copyToClipboard(code, codeIndex)}
                  sx={{
                    color: isDark ? '#abb2bf' : '#24292e',
                    '&:hover': {
                      backgroundColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.06)',
                    },
                  }}
                >
                  <ContentCopyIcon fontSize="small" />
                  {copiedCode === codeIndex && (
                    <Typography
                      variant="caption"
                      sx={{
                        ml: 1,
                        color: '#98c379',
                        fontSize: '12px',
                      }}
                    >
                      Скопировано!
                    </Typography>
                  )}
                </IconButton>
              </Box>
              {/* Подсвеченный код */}
              <Box
                sx={{
                  overflow: 'auto',
                  maxHeight: 500,
                  '& pre': {
                    margin: 0,
                    padding: '16px !important',
                  },
                }}
              >
                <SyntaxHighlighter
                  language={language}
                  style={oneDark}
                  customStyle={{
                    margin: 0,
                    padding: 0,
                    background: '#1e2127',
                    fontSize: '14px',
                    lineHeight: '1.5',
                  }}
                  showLineNumbers
                  wrapLines
                >
                  {code}
                </SyntaxHighlighter>
              </Box>
            </Paper>
          );
        },
        // Ссылки
        a({ node, ...props }) {
          return (
            <Box
              component="a"
              {...props}
              sx={{
                color: '#1976d2',
                textDecoration: 'none',
                '&:hover': {
                  textDecoration: 'underline',
                },
              }}
              target="_blank"
              rel="noopener noreferrer"
            />
          );
        },
        // Заголовки
        h1({ node, ...props }) {
          return (
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              sx={{ mt: 3, mb: 2, fontWeight: 'bold' }}
              {...props}
            />
          );
        },
        h2({ node, ...props }) {
          return (
            <Typography
              variant="h5"
              component="h2"
              gutterBottom
              sx={{ mt: 2.5, mb: 1.5, fontWeight: 'bold' }}
              {...props}
            />
          );
        },
        h3({ node, ...props }) {
          return (
            <Typography
              variant="h6"
              component="h3"
              gutterBottom
              sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}
              {...props}
            />
          );
        },
        // Параграфы
        p({ node, ...props }) {
          return (
            <Typography
              variant="body1"
              paragraph
              sx={{ my: 1, lineHeight: 1.7 }}
              {...props}
            />
          );
        },
        // Списки
        ul({ node, ...props }) {
          return (
            <Box
              component="ul"
              sx={{
                my: 1,
                pl: 3,
                '& li': {
                  my: 0.5,
                },
              }}
              {...props}
            />
          );
        },
        ol({ node, ...props }) {
          return (
            <Box
              component="ol"
              sx={{
                my: 1,
                pl: 3,
                '& li': {
                  my: 0.5,
                },
              }}
              {...props}
            />
          );
        },
        // Цитаты
        blockquote({ node, ...props }) {
          return (
            <Box
              component="blockquote"
              sx={{
                borderLeft: '4px solid #1976d2',
                pl: 2,
                py: 1,
                my: 2,
                backgroundColor: 'rgba(25, 118, 210, 0.04)',
                fontStyle: 'italic',
              }}
              {...props}
            />
          );
        },
        // Таблицы
        table({ node, ...props }) {
          return (
            <Box
              sx={{
                overflow: 'auto',
                my: 2,
                '& table': {
                  borderCollapse: 'collapse',
                  width: '100%',
                },
                '& th, & td': {
                  border: '1px solid rgba(0,0,0,0.12)',
                  padding: '8px 12px',
                  textAlign: 'left',
                },
                '& th': {
                  backgroundColor: 'rgba(0,0,0,0.02)',
                  fontWeight: 'bold',
                },
              }}
              {...props}
            />
          );
        },
      }}
    />
  );
};

export default MarkdownRenderer;
