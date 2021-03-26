function message(status, shake = false, id = "") {
  if (shake) {
    $("#" + id).effect(
      "shake",
      { direction: "right", times: 2, distance: 8 },
      250
    );
  }
  document.getElementById("feedback").innerHTML = status;
  $("#feedback").show().delay(2000).fadeOut();
}

function error(type) {
  $("." + type).css("border-color", "#E14448");
}

var login = function () {
  $.post({
    type: "POST",
    url: "/",
    data: {
      username: $("#login-user").val(),
      password: $("#login-pass").val(),
    },
    success(response) {
      var status = JSON.parse(response)["status"];
      if (status === "Login successful") {
        location.reload();
      } else {
        error("login-input");
      }
    },
  });
};

$(document).ready(function () {
  $(document).on("click", "#login-button", login);
  $(document).keypress(function (e) {
    if (e.which === 13) {
      login();
    }
  });

  $(document).on("click", "#signup-button", function () {
    $.post({
      type: "POST",
      url: "/signup",
      data: {
        username: $("#signup-user").val(),
        password: $("#signup-pass").val(),
        email: $("#signup-mail").val(),
      },
      success(response) {
        var status = JSON.parse(response)["status"];
        if (status === "Signup successful") {
          location.reload();
        } else {
          message(status, true, "signup-box");
        }
      },
    });
  });

  // $(document).on("click", "#name-button", function() {
  //   $.post({
  //     type: "POST",
  //     url: "/hello",
  //     data: {"name": $("#name-input").val()},
  //     success(response) {
  //       var status = JSON.parse(response)["greeting"];
  //       $("#greeting").text(status);
  //       console.log(status);
  //     }
  //   });
  // });

  // logic to change for uploading image

  // let base64Image;
  // $(document).on("change", "#image-selector", function() {
  //   let reader = new FileReader();
  //   reader.onload = function(e){
  //     let dataURL = reader.result;
  //     $('#selected-image').attr('src', dataURL);
  //     base64Image=dataURL.replace("data:image/png;base64,","");
  //     console.log(base64Image);
  //   }
  //   reader.readAsDataURL($('#image-selector')[0].files[0]);
  //   $('#predictions').text("");

  // });

  $(document).on("click", "#predict-button", function () {
    console.log(`working`);
    // var class_name = JSON.parse(response)["prediction"];
    // var confidence = JSON.parse(response)["confidence"];
    // $("#predictions").text(class_name);
    // $("#confidence").text(confidence);
    // console.log(class_name);
    // console.log(confidence);
  });

  $(document).on("click", "#save", function () {
    $.post({
      type: "POST",
      url: "/settings",
      data: {
        username: $("#settings-user").val(),
        password: $("#settings-pass").val(),
        email: $("#settings-mail").val(),
      },
      success(response) {
        message(JSON.parse(response)["status"]);
      },
    });
  });
});

// Open or Close mobile & tablet menu
// https://github.com/jgthms/bulma/issues/856
$("#navbar-burger-id").click(function () {
  if ($("#navbar-burger-id").hasClass("is-active")) {
    $("#navbar-burger-id").removeClass("is-active");
    $("#navbar-menu-id").removeClass("is-active");
  } else {
    $("#navbar-burger-id").addClass("is-active");
    $("#navbar-menu-id").addClass("is-active");
  }
});