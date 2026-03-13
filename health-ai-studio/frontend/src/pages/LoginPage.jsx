import {
  AlertCircle,
  CheckCircle2,
  Chrome,
  Eye,
  EyeOff,
  Github,
  Loader2
} from 'lucide-react';
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

function validate(values) {
  const errors = {};

  if (!values.email.trim()) {
    errors.email = 'Email is required.';
  } else if (!isValidEmail(values.email)) {
    errors.email = 'Enter a valid email address.';
  }

  if (!values.password) {
    errors.password = 'Password is required.';
  } else if (values.password.length < 8) {
    errors.password = 'Password must be at least 8 characters.';
  } else if (!/[A-Za-z]/.test(values.password) || !/\d/.test(values.password)) {
    errors.password = 'Password must include letters and numbers.';
  }

  return errors;
}

function ToastStack({ items, onClose }) {
  return (
    <div className="fixed right-4 top-4 z-50 w-[92vw] max-w-sm space-y-2">
      {items.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-start gap-2 rounded-xl border px-3 py-3 shadow-lg backdrop-blur ${
            toast.type === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
              : 'border-rose-200 bg-rose-50 text-rose-800'
          }`}
        >
          {toast.type === 'success' ? <CheckCircle2 className="mt-0.5 h-4 w-4" /> : <AlertCircle className="mt-0.5 h-4 w-4" />}
          <div className="flex-1">
            <p className="text-sm font-medium">{toast.message}</p>
          </div>
          <button onClick={() => onClose(toast.id)} className="text-xs font-semibold opacity-70 hover:opacity-100">
            Close
          </button>
        </div>
      ))}
    </div>
  );
}

function FloatingInput({
  id,
  label,
  type = 'text',
  value,
  onChange,
  error,
  rightAdornment,
  autoComplete
}) {
  return (
    <div className="space-y-1.5">
      <div className="relative">
        <input
          id={id}
          name={id}
          type={type}
          value={value}
          onChange={onChange}
          autoComplete={autoComplete}
          placeholder=" "
          className={`peer w-full rounded-lg border bg-white/90 px-3 py-3 text-sm text-slate-900 outline-none transition focus:border-indigo-500 focus:ring focus:ring-indigo-500/20 ${
            error ? 'border-rose-300 ring-rose-100' : 'border-gray-300'
          } ${rightAdornment ? 'pr-11' : ''}`}
          required
        />
        <label
          htmlFor={id}
          className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 rounded bg-white/80 px-1 text-sm text-slate-500 transition-all duration-150 peer-focus:top-0 peer-focus:-translate-y-1/2 peer-focus:text-xs peer-focus:text-indigo-600 peer-[:not(:placeholder-shown)]:top-0 peer-[:not(:placeholder-shown)]:-translate-y-1/2 peer-[:not(:placeholder-shown)]:text-xs"
        >
          {label}
        </label>
        {rightAdornment ? <div className="absolute inset-y-0 right-0 flex items-center pr-3">{rightAdornment}</div> : null}
      </div>
      {error ? <p className="text-xs font-medium text-rose-600">{error}</p> : null}
    </div>
  );
}

export default function LoginPage({ onLogin, onGoogleLogin, onGithubLogin }) {
  const [values, setValues] = useState({
    email: '',
    password: '',
    rememberMe: true
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [providerLoading, setProviderLoading] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [toasts, setToasts] = useState([]);

  const isBusy = loading || Boolean(providerLoading);

  const nextToastId = useMemo(() => Date.now(), [toasts.length]);

  const pushToast = (type, message) => {
    const id = `${nextToastId}-${Math.random().toString(36).slice(2, 7)}`;
    setToasts((current) => [{ id, type, message }, ...current].slice(0, 3));
    window.setTimeout(() => {
      setToasts((current) => current.filter((item) => item.id !== id));
    }, 3800);
  };

  const closeToast = (id) => {
    setToasts((current) => current.filter((item) => item.id !== id));
  };

  const handleChange = (field, value) => {
    setValues((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => ({ ...current, [field]: '' }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const errors = validate(values);
    setFieldErrors(errors);

    if (Object.keys(errors).length > 0) {
      pushToast('error', 'Please correct the highlighted fields.');
      return;
    }

    setLoading(true);
    try {
      if (onLogin) {
        await onLogin({
          email: values.email.trim(),
          password: values.password,
          rememberMe: values.rememberMe
        });
      } else {
        await new Promise((resolve) => setTimeout(resolve, 1200));
      }
      pushToast('success', 'Login successful. Redirecting...');
    } catch (error) {
      pushToast('error', error.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleProviderLogin = async (provider) => {
    setProviderLoading(provider);
    try {
      if (provider === 'google' && onGoogleLogin) {
        await onGoogleLogin();
      } else if (provider === 'github' && onGithubLogin) {
        await onGithubLogin();
      } else {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      pushToast('success', `${provider === 'google' ? 'Google' : 'GitHub'} login started.`);
    } catch (error) {
      pushToast('error', error.message || `${provider} login failed.`);
    } finally {
      setProviderLoading('');
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-[#3b82f6] via-[#6366f1] to-[#8b5cf6] px-4 py-8 sm:py-10">
      <ToastStack items={toasts} onClose={closeToast} />

      <div className="pointer-events-none absolute -left-20 top-10 h-72 w-72 animate-pulse rounded-full bg-cyan-300/20 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-80 w-80 animate-pulse rounded-full bg-fuchsia-200/20 blur-3xl" />

      <div className="flex min-h-[calc(100vh-2rem)] items-center justify-center">
        <section className="w-full max-w-[420px] rounded-3xl border border-white/35 bg-white/20 p-8 shadow-2xl shadow-slate-900/20 backdrop-blur-xl">
          <header className="mb-7 text-center">
            <h1 className="text-3xl font-semibold tracking-tight text-white">Welcome Back</h1>
            <p className="mt-2 text-sm text-indigo-100">Sign in to your Health AI Studio account</p>
          </header>

          <div className="mb-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={() => handleProviderLogin('google')}
              disabled={isBusy}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-white/40 bg-white/30 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-white/40 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {providerLoading === 'google' ? <Loader2 className="h-4 w-4 animate-spin" /> : <Chrome className="h-4 w-4" />}
              Google
            </button>

            <button
              type="button"
              onClick={() => handleProviderLogin('github')}
              disabled={isBusy}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-white/40 bg-white/30 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-white/40 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {providerLoading === 'github' ? <Loader2 className="h-4 w-4 animate-spin" /> : <Github className="h-4 w-4" />}
              GitHub
            </button>
          </div>

          <div className="mb-5 flex items-center gap-3">
            <div className="h-px flex-1 bg-white/40" />
            <span className="text-xs font-medium uppercase tracking-wide text-indigo-100">Or sign in with email</span>
            <div className="h-px flex-1 bg-white/40" />
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <FloatingInput
              id="email"
              label="Email"
              type="email"
              autoComplete="email"
              value={values.email}
              onChange={(event) => handleChange('email', event.target.value)}
              error={fieldErrors.email}
            />

            <FloatingInput
              id="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              value={values.password}
              onChange={(event) => handleChange('password', event.target.value)}
              error={fieldErrors.password}
              rightAdornment={
                <button
                  type="button"
                  onClick={() => setShowPassword((current) => !current)}
                  className="text-slate-500 transition hover:text-indigo-600"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
            />

            <div className="flex items-center justify-between gap-3 text-sm">
              <label className="inline-flex cursor-pointer items-center gap-2 text-indigo-100">
                <input
                  type="checkbox"
                  checked={values.rememberMe}
                  onChange={(event) => handleChange('rememberMe', event.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                Remember me
              </label>

              <Link to="/forgot-password" className="font-medium text-indigo-100 transition hover:text-white hover:underline">
                Forgot password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={isBusy}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-indigo-600 via-violet-600 to-fuchsia-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-900/30 transition hover:from-indigo-700 hover:via-violet-700 hover:to-fuchsia-700 disabled:cursor-not-allowed disabled:opacity-75"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <footer className="mt-6 text-center text-sm text-indigo-100">
            Don&apos;t have an account?{' '}
            <Link to="/register" className="font-semibold text-white hover:underline">
              Create account
            </Link>
          </footer>
        </section>
      </div>
    </div>
  );
}
