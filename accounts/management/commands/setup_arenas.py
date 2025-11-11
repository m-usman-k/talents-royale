from django.core.management.base import BaseCommand
from accounts.models import Arena

class Command(BaseCommand):
    help = 'Creates default arenas for Talents Royale'

    def handle(self, *args, **options):
        arenas_data = [
            {
                'name': 'Recruit Arena',
                'tier': 'recruit',
                'token_cost': 15,
                'description': 'Start your journey in the Recruit tier. Perfect for newcomers to showcase their talent and begin their rise to royalty. Entry fee: 15 tokens.',
            },
            {
                'name': 'Veteran Arena',
                'tier': 'veteran',
                'token_cost': 25,
                'description': 'Prove your skills in the Veteran tier. For those who have mastered the basics and are ready for greater challenges. Entry fee: 25 tokens.',
            },
            {
                'name': 'Champion Arena',
                'tier': 'champion',
                'token_cost': 55,
                'description': 'Compete with the best in the Champion tier. Reserved for elite performers who dominate their craft. Entry fee: 55 tokens.',
            },
            {
                'name': 'Elite Arena',
                'tier': 'elite',
                'token_cost': 100,
                'description': 'Reach the pinnacle in the Elite tier. The ultimate tier with exclusive access to Finale Royale and premium rewards. Entry fee: 100 tokens.',
            },
        ]

        created_count = 0
        updated_count = 0

        for arena_data in arenas_data:
            arena, created = Arena.objects.update_or_create(
                tier=arena_data['tier'],
                defaults={
                    'name': arena_data['name'],
                    'token_cost': arena_data['token_cost'],
                    'description': arena_data['description'],
                    'is_active': True,
                    'max_participants': 100,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created {arena.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated {arena.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully set up arenas: {created_count} created, {updated_count} updated'
            )
        )

