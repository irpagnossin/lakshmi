mongo -- "lakshmi_test" <<EOF
    db.createUser({
        user: "test",
        pwd: "test",
        roles: [
            { "role" : "readWrite", "db" : "lakshmi_test" }
        ]
    });
EOF
