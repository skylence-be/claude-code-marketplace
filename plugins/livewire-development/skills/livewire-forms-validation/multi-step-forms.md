# Multi-Step Forms

Livewire 4 form wizards with step validation and state preservation.

## Basic Multi-Step Form

```php
<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\WithFileUploads;
use Livewire\Attributes\Validate;

class UserOnboarding extends Component
{
    use WithFileUploads;

    public $currentStep = 1;
    public $totalSteps = 4;

    // Step 1: Personal Info
    #[Validate('required|min:3')]
    public $firstName = '';

    #[Validate('required|min:3')]
    public $lastName = '';

    #[Validate('required|date|before:today')]
    public $birthDate = '';

    // Step 2: Contact Info
    #[Validate('required|email|unique:users,email')]
    public $email = '';

    #[Validate('required|string')]
    public $phone = '';

    // Step 3: Account Setup
    #[Validate('required|min:8|confirmed')]
    public $password = '';

    public $password_confirmation = '';

    #[Validate('nullable|image|max:2048')]
    public $profilePhoto;

    // Step 4: Preferences
    #[Validate('required|array|min:1')]
    public $interests = [];

    #[Validate('required|accepted')]
    public $terms = false;

    /**
     * Get validation rules for specific step.
     */
    protected function getRulesForStep($step)
    {
        return match($step) {
            1 => [
                'firstName' => 'required|min:3',
                'lastName' => 'required|min:3',
                'birthDate' => 'required|date|before:today',
            ],
            2 => [
                'email' => 'required|email|unique:users,email',
                'phone' => 'required|string',
            ],
            3 => [
                'password' => 'required|min:8|confirmed',
                'profilePhoto' => 'nullable|image|max:2048',
            ],
            4 => [
                'interests' => 'required|array|min:1',
                'terms' => 'required|accepted',
            ],
            default => [],
        };
    }

    /**
     * Validate and move to next step.
     */
    public function nextStep()
    {
        $this->validate($this->getRulesForStep($this->currentStep));

        if ($this->currentStep < $this->totalSteps) {
            $this->currentStep++;
        }
    }

    /**
     * Move to previous step.
     */
    public function previousStep()
    {
        if ($this->currentStep > 1) {
            $this->currentStep--;
        }
    }

    /**
     * Jump to specific step.
     */
    public function goToStep($step)
    {
        // Validate all previous steps
        for ($i = 1; $i < $step; $i++) {
            try {
                $this->validate($this->getRulesForStep($i));
            } catch (\Exception $e) {
                session()->flash('error', 'Please complete previous steps first.');
                return;
            }
        }

        $this->currentStep = $step;
    }

    /**
     * Submit the form.
     */
    public function submit()
    {
        // Validate all steps
        for ($i = 1; $i <= $this->totalSteps; $i++) {
            $this->validate($this->getRulesForStep($i));
        }

        $photoPath = $this->profilePhoto?->store('avatars', 'public');

        $user = \App\Models\User::create([
            'first_name' => $this->firstName,
            'last_name' => $this->lastName,
            'email' => $this->email,
            'password' => bcrypt($this->password),
            'avatar' => $photoPath,
        ]);

        auth()->login($user);

        return redirect()->route('dashboard');
    }

    public function getProgressPercentage()
    {
        return ($this->currentStep / $this->totalSteps) * 100;
    }

    public function render()
    {
        return view('livewire.user-onboarding', [
            'progressPercentage' => $this->getProgressPercentage(),
        ]);
    }
}
```

## Multi-Step Form View

```blade
<div>
    {{-- Progress bar --}}
    <div class="progress-bar">
        <div class="progress" style="width: {{ $progressPercentage }}%"></div>
    </div>

    {{-- Step indicators --}}
    <div class="steps">
        @for($i = 1; $i <= $totalSteps; $i++)
            <div @class([
                'step',
                'active' => $i === $currentStep,
                'completed' => $i < $currentStep,
                'clickable' => $i <= $currentStep,
            ])
            @if($i <= $currentStep) wire:click="goToStep({{ $i }})" @endif
            >
                <span class="step-number">{{ $i }}</span>
                <span class="step-label">
                    @switch($i)
                        @case(1) Personal @break
                        @case(2) Contact @break
                        @case(3) Account @break
                        @case(4) Confirm @break
                    @endswitch
                </span>
            </div>
        @endfor
    </div>

    <form wire:submit="submit">
        {{-- Step 1 --}}
        @if($currentStep === 1)
            <div class="step-content">
                <h3>Personal Information</h3>

                <div class="form-row">
                    <div class="form-group">
                        <label>First Name</label>
                        <input type="text" wire:model.blur="firstName">
                        @error('firstName') <span class="error">{{ $message }}</span> @enderror
                    </div>

                    <div class="form-group">
                        <label>Last Name</label>
                        <input type="text" wire:model.blur="lastName">
                        @error('lastName') <span class="error">{{ $message }}</span> @enderror
                    </div>
                </div>

                <div class="form-group">
                    <label>Date of Birth</label>
                    <input type="date" wire:model.blur="birthDate">
                    @error('birthDate') <span class="error">{{ $message }}</span> @enderror
                </div>
            </div>
        @endif

        {{-- Step 2 --}}
        @if($currentStep === 2)
            <div class="step-content">
                <h3>Contact Information</h3>

                <div class="form-group">
                    <label>Email</label>
                    <input type="email" wire:model.blur="email">
                    @error('email') <span class="error">{{ $message }}</span> @enderror
                </div>

                <div class="form-group">
                    <label>Phone</label>
                    <input type="tel" wire:model.blur="phone">
                    @error('phone') <span class="error">{{ $message }}</span> @enderror
                </div>
            </div>
        @endif

        {{-- Step 3 --}}
        @if($currentStep === 3)
            <div class="step-content">
                <h3>Account Setup</h3>

                <div class="form-group">
                    <label>Password</label>
                    <input type="password" wire:model.blur="password">
                    @error('password') <span class="error">{{ $message }}</span> @enderror
                </div>

                <div class="form-group">
                    <label>Confirm Password</label>
                    <input type="password" wire:model.blur="password_confirmation">
                </div>

                <div class="form-group">
                    <label>Profile Photo (optional)</label>
                    <input type="file" wire:model="profilePhoto">
                    @if($profilePhoto)
                        <img src="{{ $profilePhoto->temporaryUrl() }}" class="preview">
                    @endif
                </div>
            </div>
        @endif

        {{-- Step 4 --}}
        @if($currentStep === 4)
            <div class="step-content">
                <h3>Confirm & Preferences</h3>

                <div class="summary">
                    <p><strong>Name:</strong> {{ $firstName }} {{ $lastName }}</p>
                    <p><strong>Email:</strong> {{ $email }}</p>
                </div>

                <div class="form-group">
                    <label>Interests</label>
                    <div class="checkbox-group">
                        <label><input type="checkbox" wire:model="interests" value="tech"> Technology</label>
                        <label><input type="checkbox" wire:model="interests" value="sports"> Sports</label>
                        <label><input type="checkbox" wire:model="interests" value="music"> Music</label>
                    </div>
                    @error('interests') <span class="error">{{ $message }}</span> @enderror
                </div>

                <div class="form-group">
                    <label>
                        <input type="checkbox" wire:model="terms">
                        I agree to the terms
                    </label>
                    @error('terms') <span class="error">{{ $message }}</span> @enderror
                </div>
            </div>
        @endif

        {{-- Navigation --}}
        <div class="form-actions">
            @if($currentStep > 1)
                <button type="button" wire:click="previousStep">Previous</button>
            @endif

            @if($currentStep < $totalSteps)
                <button type="button" wire:click="nextStep">Next</button>
            @else
                <button type="submit">Complete</button>
            @endif
        </div>
    </form>
</div>
```

## Step Components Pattern

```php
// Parent wizard component
class FormWizard extends Component
{
    public $currentStep = 1;
    public $formData = [];

    #[On('step-completed')]
    public function handleStepComplete($data)
    {
        $this->formData = array_merge($this->formData, $data);
        $this->currentStep++;
    }

    #[On('step-back')]
    public function handleStepBack()
    {
        $this->currentStep--;
    }
}

// Step component
class WizardStep1 extends Component
{
    public $name = '';
    public $email = '';

    public function next()
    {
        $this->validate([
            'name' => 'required',
            'email' => 'required|email',
        ]);

        $this->dispatch('step-completed', data: [
            'name' => $this->name,
            'email' => $this->email,
        ]);
    }
}
```

## State Persistence

```php
class PersistentWizard extends Component
{
    public $currentStep = 1;
    public $formData = [];

    public function mount()
    {
        // Restore from session
        $this->formData = session('wizard_data', []);
        $this->currentStep = session('wizard_step', 1);
    }

    public function nextStep()
    {
        $this->validate($this->getRulesForStep($this->currentStep));

        // Save to session
        session([
            'wizard_data' => $this->formData,
            'wizard_step' => $this->currentStep + 1,
        ]);

        $this->currentStep++;
    }

    public function submit()
    {
        // Clear session after submission
        session()->forget(['wizard_data', 'wizard_step']);

        // Process form...
    }
}
```
