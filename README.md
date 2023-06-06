# Memora API Guide
## Sign up
```http
POST /api/signup/
```
### Request body
```json
{
    "username": "str",
    "password": "str",
    "name": "str",
    "surname": "str",
    "email": "str",
    "gender": "str",
    "birthdate": "str",
}
```
### Response
```json
{"message": "Add new user"}
```
## Authentication Token
Each user has their own unique 10 digit token. This token will be used for every request to define a user.<br>
```http
POST /api/login/
```
### Request body
```json
{
    "username": "str",
    "password": "str"
}
```
### Response
```json
{"message": "abcde12345"}
```
## API Table
<table>
<thead>
    <tr>
        <th>Name</th>
        <th>Method</th>
        <th>Route</th>
        <th>Request headers</th>
        <th>Request body</th>
        <th>Expected result</th>
        <th>Explanation</th>
    </tr>
</thead>
<tbody>
    <tr>
        <td><b>Sign up a user</b></td>
        <td><i>POST</i></td>
        <td><i>/api/signup/</i></td>
        <td>None</td>
        <td><pre>
        {
            "username": str,
            "password": str,
            "name": str,
            "surname": str,
            "email": str,
            "gender": str,
            "birthdate": str
        }
        </pre></td>
        <td><pre>{"message": "Add new user"}</pre></td>
        <td>-</td>
    </tr>
    <tr>
        <td><b>Get a token</b></td>
        <td><i>POST</i></td>
        <td><i>/api/login/</i></td>
        <td>None</td>
        <td><pre>
        {
            "username": str,
            "password": str
        }
        </pre></td>
        <td><pre>{"message": "abcde12345"(example of token)}</pre></td>
        <td>-</td>
    </tr>
</tbody>
</table>
