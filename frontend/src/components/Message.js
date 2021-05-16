import React from "react";
import Alert from "react-bootstrap/Alert";

function Message({ variant, children }) {
  return (
    <Alert className="text-center" variant={variant}>
      {children}
    </Alert>
  );
}

export default Message;
