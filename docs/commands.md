# aws-plugin-bucket-policy commands

## get-policy
 Return active bucket policy in JSON format.
 ### Important options
 * `--bucket`
   ... (string) Bucket name, if omitted display selection from existing buckets

---
## new-policy
 Generate and save policy to specified bucket from use-case template.
 #### Important options
 * `--bucket`
   ... (string) Bucket name, if omitted display selection from existing buckets
 * `--newpol-type`
   ... (string) New bucket policy use-case.
    * `ro-public`: public read-only bucket;
    * `share-w-user`: bucket shared with  specified  users;
    * `share-w-tenant`:  bucket shared with all users from specified tenants.
    * `share-prefix-w-user`: prefix in bucket shared with specified users;

 * `--newpol-spec`
   ... (string) New bucket policy use-case  specification.
   	* newpol-type `ro-public`: not applicable
   	* newpol-type `share-w-user`:
   	    `tenant=TENANT_NAME,user=USER_NAME,action=[rw|ro]` can  be  repeated
   	* newpol-type `share-w-tenant`:
        `tenant=TENANT_NAME,action=[rw|ro]` can be repeated
    * newpol-type `share-prefix-w-user`:
        `tenant=TENANT_NAME,user=USER_NAME,action=[rw|ro],prefix=PREFIX`
        can be repeated,
        prefix could contain url-like "%hex" characters
        (e.g. "=" as "%3d" and "%" as "%%")

---
## put-policy
 Save JSON-formatted policy to specified bucket.
 ### Important options
 * `--bucket`
   ... (string) Bucket name, if omitted display selection from existing buckets
 * `--policy`
   ... (string) Policy file name

---
## delete-policy
 Delete active bucket policy from specified bucket.
 ### Important options
 * `--bucket`
   ... (string) Bucket name, if omitted display selection from existing buckets

---
## Global options
 * `--profile`
   ... (string) Use a specific profile from your credential file
 * `--nofzf`
   ... (boolean) Disable [fzf](https://github.com/dahlia/iterfzf) support
 * `--nonint`
   ... (boolean) Disable interactive UI
 * `--quiet`
   ... (boolean) Low verbosity output
 * `--dryrun`
   ... (boolean) Dry-run with all write operations disabled
