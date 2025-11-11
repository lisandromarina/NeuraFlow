import LoginPage from '../pages/login';
import RegisterPage from '../pages/register';
import LandingPage from '../pages/landing';
import Layout from '../components/layout';
import OAuthSuccessPage from '../pages/oauth-success';
import { Route, Routes } from 'react-router-dom';
import PublicRoute from './PublicRoute';
import PrivateRoute from './PrivateRoute';

function RouterContainer() {
  return (
    <Routes>
      <Route path="/" element={<PublicRoute />}>
        <Route index element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      <Route path="/" element={<PrivateRoute />}>
        <Route path="/workflow" element={<Layout />} />
      </Route>

      <Route path="/oauth-success" element={<OAuthSuccessPage />} />
    </Routes>
  );
}

export default RouterContainer;
