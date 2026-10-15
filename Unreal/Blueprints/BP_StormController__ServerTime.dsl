; Match clock shared by server and clients
(fn ServerTime ()
  (return (GameState|GetServerWorldTimeSeconds :self (Game|GetGameState))))
