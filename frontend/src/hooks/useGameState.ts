import { useCallback, useState } from "react";

import { createInitialState, makeChoice } from "../game/gameLogic";
import type { ChoiceType, GameState } from "../game/types";

export function useGameState() {
  const [state, setState] = useState<GameState>(() => createInitialState());
  const [showBankruptcyOverlay, setShowBankruptcyOverlay] = useState(false);

  const makeLocalChoice = useCallback((choice: ChoiceType) => {
    let shouldShowOverlay = false;
    setState((current) => {
      const next = makeChoice(current, choice);
      shouldShowOverlay = next.gameOver && next.gameOverReason === "bankruptcy";
      return next;
    });
    if (shouldShowOverlay) {
      setShowBankruptcyOverlay(true);
    }
  }, []);

  const resetGame = useCallback(() => {
    setState(createInitialState());
    setShowBankruptcyOverlay(false);
  }, []);

  const dismissBankruptcyOverlay = useCallback(() => {
    setShowBankruptcyOverlay(false);
  }, []);

  return {
    state,
    setState,
    makeLocalChoice,
    resetGame,
    showBankruptcyOverlay,
    dismissBankruptcyOverlay
  };
}
