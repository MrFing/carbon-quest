import { Navigate, Route, Routes } from "react-router-dom";

import TitleScreen from "./components/TitleScreen";
import LocalGame from "./components/LocalGame";
import OnlineGame from "./components/OnlineGame";
import CreateParty from "./components/CreateParty";
import OnlineSessionPage from "./components/OnlineSessionPage";

export default function App() {
  return (
    <div className="app-shell">
      <Routes>
        <Route path="/" element={<TitleScreen />} />
        <Route path="/local" element={<LocalGame />} />
        <Route path="/online" element={<OnlineGame />} />
        <Route path="/party/:code" element={<CreateParty />} />
        <Route path="/game/:sessionId" element={<OnlineSessionPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  );
}
