<h1>Memora API Guide</h1>
<h2>Sign up</h2>
<p>To sign up a new user you have to do a POST request to <code>/api/signup/</code><br>
Request body requirements:<br>
<code>{<br>
    "username": str,<br>
    "password": str,<br>
    "name": str,<br>
    "surname": str,<br>
    "email": str,<br>
    "gender": str,<br>
    "birthdate": str,<br>
}<br></code>
If everything went good you will receive this response:<br>
<code>{"message": "Add new user"}</code><br></p>
<h2>Authentication Token</h2>
<p>Each user has their own unique 10 digit token. This token will be used for every request to define a user.<br>
To get an Authentication Token you have to do a POST request to <code>/api/login/</code><br>
Request body requirements:<br>
<code>{<br>
    "username": str,<br>
    "password": str,<br>
}<br>
</code>
If everything went good you will receive a response like this:<br>
<code>{"message": "abcde12345"(example of token)}</code><br></p>
<h2>API Table</h2>
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
        <td>Sign up a user</td>
        <td>POST</td>
        <td>/api/signup/</td>
        <td>None</td>
        <td>
        <code>{<br>
            "username": str,<br>
            "password": str,<br>
            "name": str,<br>
            "surname": str,<br>
            "email": str,<br>
            "gender": str,<br>
            "birthdate": str,<br>
        }</code></td>
        <td><code>{"message": "Add new user"}</code></td>
    </tr>
    <tr>
        <td>Get a token</td>
        <td>POST</td>
        <td>/api/login/</td>
        <td>None</td>
        <td>
        <code>{<br>
            "username": str,<br>
            "password": str,<br>
        }</code></td>
        <td><code>{"message": "abcde12345"(example of token)}</code></td>
    </tr>
</tbody>
</table>