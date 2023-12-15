mongo -- "lakshmi" <<EOF
    db.createCollection("positions");
    db.positions.insertOne({
        "position_id": 1,
        "carreer_id": 1,
        "traits": {
            "11": [1],
            "12": [2, 3]
        },
        "weights": {
            "11": 20,
            "12": 80
        },
        "created_at": "2022-06-13T20:50:26.701495",
        "updated_at": null,
        "dirty": false
    });

    db.createUser({
        user: "api",
        pwd: "api",
        roles: [
            { "role" : "readWrite", "db" : "lakshmi" }
        ]
    });
EOF
