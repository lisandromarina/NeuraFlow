import LoginPage from '../components/login';
import Layout from '../components/layout';
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

        </Routes>
    );
}

export default RouterContainer;