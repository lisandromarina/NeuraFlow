import LoginPage from '../components/login';
import Layout from '../components/layout';
import { Route, Routes } from 'react-router-dom';


function RouterContainer() {
    return (
        <Routes>

            <Route path="/" element={<Layout />} />

            <Route path="/login" element={<LoginPage />} />

        </Routes>
    );
}

export default RouterContainer;