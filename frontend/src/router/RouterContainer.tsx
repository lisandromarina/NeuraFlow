import LoginPage from '../components/login';
import Layout from '../components/layout';
import OAuthSuccessPage from '../pages/oauth-success';
import { Route, Routes } from 'react-router-dom';
import PublicRoute from './PublicRoute';
import PrivateRoute from './PrivateRoute';

function RouterContainer() {
  return (
    <Routes>
      <Route path="/" element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      <Route path="/" element={<PrivateRoute />}>
        <Route path="/workflow" element={<Layout />} />
      </Route>

      <Route path="/oauth-success" element={<OAuthSuccessPage />} />
    </Routes>
  );
}

export default RouterContainer;
