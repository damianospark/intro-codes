import React from "react";
import logo from "./logo.svg";
import "./App.css";
import UTMGenerator from "./UTMGenerator";

function App() {
    const [userId, setUserId] = React.useState("");
    // React.useEffect(() => {
    //     fetch('/auth')
    //       .then((response) => {
    //         if (response.ok) {
    //           return response.json();
    //         } else {
    //           console.log('response',response.json());
    //           throw new Error('Failed to fetch user ID');

    //         }
    //       })
    //       .then((data) => {
    //         setUserId(data.userId);
    //       })
    //       .catch((error) => {
    //         console.error('cathed error: ',error);

    //       });
    //   }, []);

    return (
        <div className="App">
            <UTMGenerator user={userId} />
        </div>
    );
}

export default App;
