// Function to get the value of a URL parameter
function getUrlParameter(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)");
  var results = regex.exec(location.search);
  return results === null
    ? ""
    : decodeURIComponent(results[1].replace(/\+/g, " "));
}

const loggedInUserId = getUrlParameter("userId");
console.log(loggedInUserId);

// Define Hashing Function:
function hashFunction(userID) {
  var hashValue = Array.from(userID).reduce(
    (acc, char) => acc + char.charCodeAt(0),
    0,
  );
  return hashValue % 3;
}

// Hash
var databaseNum = hashFunction(loggedInUserId);
console.log(databaseNum);

// Prepare URL
var dbUrl = "";
if (databaseNum === 0) {
  dbUrl =
    "https://hospital1-850e0-default-rtdb.firebaseio.com/users/" +
    loggedInUserId +
    ".json"; // database 1 link
} else if (databaseNum === 1) {
  dbUrl =
    "https://hospital-2-f901a-default-rtdb.firebaseio.com/users/" +
    loggedInUserId +
    ".json"; // database 2 link
} else if (databaseNum === 2) {
  dbUrl =
    "https://hospital-3-502e9-default-rtdb.firebaseio.com/users/" +
    loggedInUserId +
    ".json"; // database 3 link
}

// Send GET request to fetch user data
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
      // Display info
      document.getElementById("user-name").textContent = userData.name;
      document.getElementById("user-gender").textContent = userData.gender;
      document.getElementById("user-age").textContent = userData.age;
      document.getElementById("user-phone").textContent = userData.phone_number;
      document.getElementById("user-medication").textContent =
        userData.medication;
      document.getElementById("user-allergies").textContent =
        userData.allergies;

      // Set loggedName here
      const loggedInUserId = getUrlParameter("userId");

      // Set the href with the user_name
      const makeAppointmentBtn = document.getElementById("make-appointment");
      makeAppointmentBtn.onclick = function () {
        window.location.href = `make_appointment.html?userId=${loggedInUserId}`;
      };

      const changeAppointmentBtn =
        document.getElementById("change-appointment");
      changeAppointmentBtn.onclick = function () {
        window.location.href = `change_appointment.html?userId=${loggedInUserId}`;
      };

      const cancelAppointmentBtn =
        document.getElementById("cancel-appointment");
      cancelAppointmentBtn.onclick = function () {
        window.location.href = `cancel_appointment.html?userId=${loggedInUserId}`;
      };
    }
  })
  .catch((error) => {
    console.error("There was a problem with the fetch operation:", error);
  });
