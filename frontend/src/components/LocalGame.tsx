import { useNavigate } from "react-router-dom";

import GameBoard from "./GameBoard";
import { useGameState } from "../hooks/useGameState";

export default function LocalGame() {
  const navigate = useNavigate();
  const { state, makeLocalChoice, resetGame, showBankruptcyOverlay, dismissBankruptcyOverlay } = useGameState();
  const currentBudget = state.currentPlayer === 1 ? state.player1.budget : state.player2.budget;

  return (
    <GameBoard
      state={state}
      canPlay={!state.gameOver}
      currentBudget={currentBudget}
      onChoice={makeLocalChoice}
      onPlayAgain={resetGame}
      onQuit={() => navigate("/")}
      showBankruptcyOverlay={showBankruptcyOverlay}
      onDismissBankruptcyOverlay={dismissBankruptcyOverlay}
    />
  );
}
