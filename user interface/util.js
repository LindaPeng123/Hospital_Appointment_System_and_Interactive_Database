
// use the fetch function based on different filter conditions to send requests to the Firebase database and get data

async function queryAppointmentsByDate(date, url) {
  return fetch(`${url}.json?orderBy="date"&equalTo="${date}"`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) => Object.values(response).map((data) => data.time));
}

async function queryAppointmentsByUserId(userId, url) {
  return fetch(`${url}.json?orderBy="userId"&equalTo="${userId}"`, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((response) =>
      Object.entries(response).map(([key, value]) => {
        return {
          id: key,
          date: value.date,
          time: value.time,
          reason: value.reason,
          userId: value.userId,
        };
      }),
    );
}

// Delete appointment by id
async function deleteAppointmentsById(id, url) {
  return fetch(
    `${url}/${id}.json`,
    {
      method: "DELETE",
    },
    {
      method: "DELETE",
    },
  );
}

// update appointments
async function updateAppointment(id, userId, date, time, reason, url) {
  return fetch(`${url}/${id}.json`, {
    method: "PUT",
    body: JSON.stringify({
      userId,
      date,
      time,
      reason,
    }),
  });
}

function getUserId() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("userId");
}
