// Listen for form submission
document.getElementById("login-form").addEventListener("submit", submitForm);

function submitForm(e) {
  e.preventDefault();

  // Get values
  var username = getElementVal("userid");
  var password = getElementVal("password");

  // Hash the username
  var databaseNum = hashFunction(username);

  // Prepare URL
  var dbUrl = "";
  if (databaseNum === 0) {
    dbUrl =
      "https://hospital1-850e0-default-rtdb.firebaseio.com/users/" +
      username +
      ".json"; // database 1 link
  } else if (databaseNum === 1) {
    dbUrl =
      "https://hospital-2-f901a-default-rtdb.firebaseio.com/users/" +
      username +
      ".json"; // database 2 link
  } else if (databaseNum === 2) {
    dbUrl =
      "https://hospital-3-502e9-default-rtdb.firebaseio.com/users/" +
      username +
      ".json"; // database 3 link
  }

  // Send GET request to check if username exists
  fetch(dbUrl)
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error("Network response was not ok.");
      }
    })
    .then((userData) => {
      if (userData !== null) {
        // User exists, now check password
        if (userData.password === password) {
          // Password is correct, redirect to user_portal.html
          const loggedInUserId = username;
          window.location.href = `user_portal.html?userId=${loggedInUserId}`;
        } else {
          // Incorrect password
          alert("Incorrect password. Please try again.");
        }
      } else {
        // Username does not exist
        alert("Username not found. Please register first.");
      }
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
      // Handle errors, e.g., showing an error message
    });
}

// Function to get form values
function getElementVal(id) {
  return document.getElementById(id).value;
}

// Define Hashing Function:
function hashFunction(userID) {
  var hashValue = Array.from(userID).reduce(
    (acc, char) => acc + char.charCodeAt(0),
    0,
  );
  return hashValue % 3;
}
