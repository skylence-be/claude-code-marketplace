# SQL Injection Prevention

Protect against database injection attacks.

## Use Eloquent (Safe)

```php
// SAFE - Eloquent uses prepared statements
User::where('email', $email)->first();
User::where('id', $id)->update(['name' => $name]);
Post::whereIn('id', $ids)->get();
```

## Query Builder with Bindings (Safe)

```php
// SAFE - Named bindings
DB::select('SELECT * FROM users WHERE email = :email', [
    'email' => $email
]);

// SAFE - Positional bindings
DB::select('SELECT * FROM users WHERE email = ?', [$email]);

// SAFE - Where clause with value
DB::table('users')->where('email', '=', $email)->first();
```

## Dangerous Patterns (Avoid)

```php
// DANGEROUS - Direct interpolation
DB::select("SELECT * FROM users WHERE email = '$email'");

// DANGEROUS - Raw in where
DB::table('users')->whereRaw("email = '$email'")->first();

// DANGEROUS - Unbound orderBy
DB::table('users')->orderBy($userInput)->get();
```

## Safe Raw Queries

```php
// SAFE - Raw with bindings
DB::table('users')
    ->whereRaw('email = ?', [$email])
    ->get();

// SAFE - selectRaw with bindings
DB::table('orders')
    ->selectRaw('SUM(amount) as total')
    ->whereRaw('user_id = ? AND status = ?', [$userId, 'completed'])
    ->first();

// SAFE - orderByRaw with whitelist
$allowed = ['name', 'created_at', 'email'];
$column = in_array($request->sort, $allowed) ? $request->sort : 'created_at';
DB::table('users')->orderBy($column)->get();
```

## Whitelist Column Names

```php
class UserController extends Controller
{
    protected array $sortableColumns = ['name', 'email', 'created_at'];
    protected array $searchableColumns = ['name', 'email'];

    public function index(Request $request)
    {
        $query = User::query();

        // Safe sorting
        $sortBy = in_array($request->sort_by, $this->sortableColumns)
            ? $request->sort_by
            : 'created_at';
        $query->orderBy($sortBy, $request->boolean('desc') ? 'desc' : 'asc');

        // Safe searching
        if ($request->search && $request->search_field) {
            $field = in_array($request->search_field, $this->searchableColumns)
                ? $request->search_field
                : 'name';
            $query->where($field, 'like', '%' . $request->search . '%');
        }

        return $query->paginate();
    }
}
```

## JSON Column Safety

```php
// SAFE - Eloquent JSON syntax
User::where('settings->theme', 'dark')->get();

// SAFE - JSON contains
User::whereJsonContains('roles', 'admin')->get();

// DANGEROUS - Raw JSON path from user
DB::table('users')
    ->whereRaw("JSON_EXTRACT(settings, '$.$userInput') = ?", [$value])
    ->get();
```

## Mass Assignment Protection

```php
class User extends Model
{
    // Whitelist (recommended)
    protected $fillable = ['name', 'email', 'bio'];

    // Or blacklist
    protected $guarded = ['id', 'role', 'is_admin', 'password'];
}

// Safe usage
$user->fill($request->only(['name', 'email', 'bio']));
$user->fill($request->validated()); // From Form Request
```
