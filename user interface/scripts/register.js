document.getElementById("register-form").addEventListener("submit", submitForm);

function submitForm(e) {
  e.preventDefault();

  var userid = getElementVal("userid");
  var firstname = getElementVal("firstname");
  var lastname = getElementVal("lastname");
  var email = getElementVal("email");
  var phone = getElementVal("phone");
  var allergies = getElementVal("allergies");
  var medication = getElementVal("medication");
  var dob = getElementVal("dob");
  var password = getElementVal("password");
  var gender = document.getElementById("gender").value; // Get gender value

  // Calculate age based on date of birth
  var age = calculateAge(dob);

  // Hash function
  function hashFunction(userID) {
    var hashValue = Array.from(userID).reduce(
      (acc, char) => acc + char.charCodeAt(0),
      0,
    );
    return hashValue % 3;
  }

  // Hash
  var databaseNum = hashFunction(userid);

  // Check if user ID already exists
  checkUserID(databaseNum, userid)
    .then((exists) => {
      if (exists) {
        alert(
          "User ID already exists in the database. Please choose a different one.",
        );
      } else {
        // Save user data
        saveMessages(
          databaseNum,
          userid,
          firstname,
          lastname,
          age,
          email,
          phone,
          allergies,
          medication,
          dob,
          password,
          gender,
        );
      }
    })
    .catch((error) => {
      console.error("Error checking user ID:", error);
    });
}

// calculate age
function calculateAge(dob) {
  console.log(Date(dob));
  var dobDate = new Date(dob);
  var currentDate = new Date();
  // console.log(dobDate);
  var age = currentDate.getFullYear() - dobDate.getFullYear();
  //console.log(age);
  var monthDiff = currentDate.getMonth() - dobDate.getMonth();
  if (
    monthDiff < 0 ||
    (monthDiff === 0 && currentDate.getDate() < dobDate.getDate())
  ) {
    age--;
  }
  //console.log(age)
  return age;
}

function checkUserID(databaseNum, userId) {
  var dbUrl = "";
  if (databaseNum === 0) {
    dbUrl = "https://hospital1-850e0-default-rtdb.firebaseio.com/users"; // database 1 link
  } else if (databaseNum === 1) {
    dbUrl = "https://hospital-2-f901a-default-rtdb.firebaseio.com/users"; // database 2 link
  } else if (databaseNum === 2) {
    dbUrl = "https://hospital-3-502e9-default-rtdb.firebaseio.com/users"; // database 3 link
  }
  var fbUrl = `${dbUrl}/${userId}.json`;

  return fetch(fbUrl)
    .then((response) => response.json())
    .then((data) => {
      return data !== null;
    })
    .catch((error) => {
      throw error;
    });
}

function saveMessages(
  databaseNum,
  userId,
  firstname,
  lastname,
  age,
  email,
  phone,
  allergies,
  medication,
  dob,
  password,
  gender,
) {
  var dbUrl = "";
  if (databaseNum === 0) {
    dbUrl = "https://hospital1-850e0-default-rtdb.firebaseio.com/users"; // database 1 link
  } else if (databaseNum === 1) {
    dbUrl = "https://hospital-2-f901a-default-rtdb.firebaseio.com/users"; // database 2 link
  } else if (databaseNum === 2) {
    dbUrl = "https://hospital-3-502e9-default-rtdb.firebaseio.com/users"; // database 3 link
  }

  var fbUrl = `${dbUrl}/${userId}.json`;

  var userData = {
    name: firstname + " " + lastname,
    password: password,
    age: age,
    email: email,
    phone_number: phone,
    allergies: allergies,
    medication: medication,
    "date of birth": dob,
    gender: gender,
  };

  // Send data to Firebase using PUT request
  return fetch(fbUrl, {
    method: "PUT",
    body: JSON.stringify(userData),
  })
    .then((response) => {
      if (response.ok) {
        document.querySelector(".alert").style.display = "block";

        setTimeout(() => {
          document.querySelector(".alert").style.display = "none";
        }, 3000);

        document.getElementById("register-form").reset();
      } else {
        console.error("Failed to save user data. Status:", response.status);
      }
    })
    .catch((error) => {
      console.error("Failed to save user data:", error);
    });
}

function getElementVal(id) {
  return document.getElementById(id).value;
}
