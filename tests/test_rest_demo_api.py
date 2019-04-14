import unittest
from os import environ as os_environ
from uuid import uuid4

import rest_demo_api


class Tests(unittest.TestCase):
    def setUp(self):
        os_environ["REST_DEMO_API_FLASK_DEBUG"] = "True"
        os_environ["REST_DEMO_API_FLASK_TESTING"] = "True"
        # RAM DB
        os_environ["REST_DEMO_API_FLASK_SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        self.app = rest_demo_api.get_app()
        self.client = self.app.test_client()

    def tearDown(self):
        del self.client
        del self.app

    def testPass(self):
        self.assertEqual(True, True)

    def testVersionAvailable(self):
        x = getattr(rest_demo_api, "__version__", None)
        self.assertTrue(x is not None)

    def testLivenessCheck(self):
        resp = self.client.get("/-/alive")
        self.assertEqual(resp.status_code, 204)

    def testHealthCheck(self):
        resp = self.client.get("/-/healthy")
        self.assertEqual(resp.status_code, 204)

    def test_add_author_no_quotes(self):
        create_resp = self.client.post(
            "/authors", json={"name": "Brian {}".format(uuid4().hex)}
        )
        self.assertEqual(create_resp.status_code, 200)
        get_resp = self.client.get("/authors/{}".format(str(create_resp.json["id"])))
        self.assertEqual(create_resp.json, get_resp.json)

    def test_add_author_with_quotes(self):
        create_resp = self.client.post(
            "/authors",
            json={
                "name": "Brian {}".format(uuid4().hex),
                "quotes": [
                    {"content": "I like python"},
                    {"content": "Marshmallow is cool"},
                ],
            },
        )
        self.assertEqual(create_resp.status_code, 200)
        get_resp = self.client.get("/authors/{}".format(str(create_resp.json["id"])))
        self.assertEqual(create_resp.json, get_resp.json)

    def test_list_authors(self):
        create_resp = self.client.post(
            "/authors", json={"name": "Brian {}".format(uuid4().hex)}
        )
        self.assertEqual(create_resp.status_code, 200)
        get_resp = self.client.get("/authors")
        create_resp.json.pop("quotes")
        self.assertTrue(create_resp.json in get_resp.json)

    def test_delete_author(self):
        create_resp = self.client.post(
            "/authors", json={"name": "Brian {}".format(uuid4().hex)}
        )
        self.assertEqual(create_resp.status_code, 200)
        get_resp = self.client.get("/authors")
        create_resp.json.pop("quotes")
        self.assertTrue(create_resp.json in get_resp.json)
        del_resp = self.client.delete("/authors/{}".format(str(create_resp.json["id"])))
        self.assertEqual(del_resp.status_code, 204)
        get_resp2 = self.client.get("/authors")
        self.assertTrue(create_resp.json not in get_resp2.json)

    def test_delete_quote(self):
        create_resp = self.client.post(
            "/quotes", json={"content": uuid4().hex, "author": {"name": uuid4().hex}}
        )
        self.assertEqual(create_resp.status_code, 200)
        del_resp = self.client.delete("/quotes/{}".format(str(create_resp.json["id"])))
        self.assertEqual(del_resp.status_code, 204)
        self.assertTrue(
            create_resp.json["id"]
            not in [x["id"] for x in self.client.get("/quotes").json]
        )

    def test_add_quote_with_existing_author(self):
        create_resp = self.client.post(
            "/authors", json={"name": "Brian {}".format(uuid4().hex)}
        )
        self.assertEqual(create_resp.status_code, 200)
        create_resp = self.client.post(
            "/quotes",
            json={
                "author": {
                    "name": create_resp.json["name"],
                    "id": create_resp.json["id"],
                },
                "content": uuid4().hex,
            },
        )
        self.assertEqual(create_resp.status_code, 200)
        get_resp = self.client.get("/quotes/{}".format(str(create_resp.json["id"])))
        self.assertEqual(create_resp.json, get_resp.json)

    def test_add_quote_with_new_author(self):
        create_resp = self.client.post(
            "/quotes",
            json={
                "author": {"name": "Brian {}".format(uuid4().hex)},
                "content": uuid4().hex,
            },
        )
        self.assertEqual(create_resp.status_code, 200)
        get_resp = self.client.get("/quotes/{}".format(str(create_resp.json["id"])))
        self.assertEqual(create_resp.json, get_resp.json)
        get_author_resp = self.client.get(
            "/authors/{}".format(str(get_resp.json["author"]["id"]))
        )
        self.assertEqual(get_author_resp.status_code, 200)

    def test_update_author(self):
        create_resp = self.client.post(
            "/authors", json={"name": "Brian {}".format(uuid4().hex)}
        )
        self.assertEqual(create_resp.status_code, 200)
        get_resp = self.client.get("/authors/{}".format(str(create_resp.json["id"])))
        self.assertEqual(create_resp.json, get_resp.json)
        new_name = create_resp.json["name"] + uuid4().hex
        put_resp = self.client.put(
            "/authors/{}".format(str(create_resp.json["id"])),
            json={"id": create_resp.json["id"], "name": new_name},
        )
        print(put_resp.json)
        self.assertEqual(put_resp.status_code, 200)
        get_resp2 = self.client.get("/authors/{}".format(str(create_resp.json["id"])))
        self.assertEqual(put_resp.json, get_resp2.json)

    def test_cant_update_quote_while_updating_author(self):
        pass

    def test_update_quote(self):
        pass

    def test_cant_update_author_while_updating_quote(self):
        pass

    def test_cant_read_a_nonexistent_author(self):
        pass

    def test_cant_read_a_nonexistent_quote(self):
        pass

    def test_cant_update_a_nonexistent_author(self):
        pass

    def test_cant_update_a_nonexistent_quote(self):
        pass

    def test_cant_delete_a_nonexistent_author(self):
        pass

    def test_cant_delete_a_nonexistent_quote(self):
        pass

    def test_all_author_endpoints_use_schema(self):
        pass

    def test_all_quote_endpoints_use_schema(self):
        pass

    def test_cant_duplicate_authors(self):
        pass

    def test_cant_duplicate_quotes(self):
        pass


if __name__ == "__main__":
    unittest.main()
