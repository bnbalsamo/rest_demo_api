import unittest
from os import environ as os_environ
from uuid import uuid4

import rest_demo_api

# We need these because the url_for function doesn't
# like to work without an application context, so we
# duplicated these values here for sorting out the keys
# from create actions that will appear in the lists.
# Keep these in sync with the "only" tuplein the schemas.

author_list_json_keys = ["name", "id", "url"]
quote_list_json_keys = ["id", "url", "content"]


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

    def test_add_author(self):
        create_resp = self.client.post(
            "/authors", json={"name": "Brian {}".format(uuid4().hex)}
        )
        self.assertEqual(create_resp.status_code, 200)
        get_resp = self.client.get("/authors/{}".format(str(create_resp.json["id"])))
        self.assertEqual(create_resp.json, get_resp.json)
        return get_resp.json

    def test_list_authors(self):
        authors = []
        for _ in range(4):
            authors.append(self.test_add_author())
        get_resp = self.client.get("/authors")
        for author in authors:
            list_json = {x: author[x] for x in author_list_json_keys}
            self.assertTrue(list_json in get_resp.json)

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
        self.assertEqual(put_resp.status_code, 200)
        get_resp2 = self.client.get("/authors/{}".format(str(create_resp.json["id"])))
        self.assertEqual(put_resp.json, get_resp2.json)
        self.assertNotEqual(get_resp.json["name"], get_resp2.json["name"])

    def test_delete_author(self):
        author = self.test_add_author()
        del_resp = self.client.delete("/authors/{}".format(str(author["id"])))
        self.assertEqual(del_resp.status_code, 204)
        get_resp2 = self.client.get("/authors")
        self.assertTrue(author not in get_resp2.json)

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
        return create_resp.json

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
        return create_resp.json

    def test_list_quotes(self):
        quotes = []
        for _ in range(4):
            quotes.append(self.test_add_quote_with_new_author())
        get_resp = self.client.get("/quotes")
        for quote in quotes:
            list_json = {x: quote[x] for x in quote_list_json_keys}
            self.assertTrue(list_json in get_resp.json)

    def test_update_quote(self):
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
        new_content = uuid4().hex
        update_resp = self.client.put(
            "/quotes/{}".format(str(create_resp.json["id"])),
            json={
                "content": new_content,
                "author": {"name": create_resp.json["author"]["name"]},
            },
        )
        self.assertEqual(update_resp.status_code, 200)
        get_resp2 = self.client.get("/quotes/{}".format(str(create_resp.json["id"])))
        self.assertEqual(get_resp2.json, update_resp.json)
        self.assertNotEqual(get_resp.json["content"], get_resp2.json["content"])

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

    def test_list_author_quotes(self):
        quotes = []
        for _ in range(4):
            quotes.append(self.test_add_quote_with_new_author())
        author_quote_resp = self.client.get(
            "/authors/{}/quotes".format(quotes[0]["author"]["id"])
        )
        # Quotes are author specific, we only see one
        self.assertEqual(len(author_quote_resp.json), 1)
        self.assertEqual(author_quote_resp.json[0]["content"], quotes[0]["content"])

    def test_create_author_quote(self):
        author_json = self.test_add_author()
        create_resp = self.client.post(
            "/authors/{}/quotes".format(str(author_json["id"])),
            json={"content": uuid4().hex},
        )
        self.assertEqual(create_resp.status_code, 200)

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

    def test_deleting_an_author_deletes_their_quotes(self):
        pass

    def test_partial_update_quote(self):
        pass

    def test_partial_update_author(self):
        pass


if __name__ == "__main__":
    unittest.main()
