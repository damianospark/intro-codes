const express = require('express');
const cors = require('cors');
const path = require('path');
const bodyParser = require('body-parser');


const app = express();
const PORT = process.env.PORT || 3001;
app.use(bodyParser.json());
app.use(cors());

// Serve the static React app files
app.use('/utm', express.static(path.join(__dirname, '../clean-utm/build')));
// Serve the static files from the React app under /utm
app.use('/utm/static', express.static(path.join(__dirname, '../clean-utm/build/static')));
app.use('/static', express.static(path.join(__dirname, '../clean-utm/build/static')));
app.use('/utm/manifest.json', express.static(path.join(__dirname, '../clean-utm/public/manifest.json')));

app.get('/auth', (req, res) => {
  const requestData = {
    headers: req.headers,
    body: req.body
  };
  console.log(requestData);
  if (requestData.headers.authorization) {
    const userId = requestData.headers['x-authenticated-user'];
    console.log('userId -->',userId)
    res.send({ userId: userId });
  } else {
    res.sendStatus(401);
  }
});
// Catch-all route for React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../clean-utm/build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
