import time
import threading
import os
import sys
import calendar
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Automated backup service that runs on the last day of each month'

    def add_arguments(self, parser):
        parser.add_argument('--time', type=str, default='23:00',
                          help='Backup time in HH:MM format (default: 23:00)')
        parser.add_argument('--daemon', action='store_true',
                          help='Run as daemon in background')
        parser.add_argument('--log-file', type=str, default='monthly_backup.log',
                          help='Log file path')
        parser.add_argument('--test-mode', action='store_true',
                          help='Test mode - runs backup every minute for testing')

    def handle(self, *args, **options):
        backup_time = options['time']
        log_file = options['log_file']
        test_mode = options['test_mode']
        
        self.stdout.write(self.style.SUCCESS(
            f'╔══════════════════════════════════════════════════════════╗'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'║           STAR SPACE MONTHLY BACKUP SERVICE              ║'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'╠══════════════════════════════════════════════════════════╣'
        ))
        if test_mode:
            self.stdout.write(self.style.SUCCESS(
                f'║  Mode: TEST MODE (every minute)                        ║'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'║  Schedule: Last day of each month at {backup_time}          ║'
            ))
        self.stdout.write(self.style.SUCCESS(
            f'║  Started: {datetime.now().strftime("%Y-%m-%d %H:%M")}                 ║'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'╚══════════════════════════════════════════════════════════╝'
        ))
        
        # Create backups directory if it doesn't exist
        backup_dir = Path(__file__).resolve().parent.parent.parent.parent / 'backups'
        monthly_dir = backup_dir / 'monthly'
        monthly_dir.mkdir(exist_ok=True, parents=True)
        
        if options['daemon']:
            # Run in background thread
            thread = threading.Thread(target=self.run_scheduler, args=(backup_time, log_file, test_mode))
            thread.daemon = True
            thread.start()
            
            self.stdout.write(self.style.SUCCESS(
                f'✅ Monthly backup service running in background (PID: {os.getpid()})'
            ))
            self.stdout.write(self.style.WARNING(
                'Press Ctrl+C to stop the service'
            ))
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING(
                    f'\n🛑 Backup service stopped at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
                ))
        else:
            # Run in foreground
            self.run_scheduler(backup_time, log_file, test_mode)

    def run_scheduler(self, backup_time, log_file, test_mode=False):
        """Run the backup scheduler"""
        self.stdout.write(f"📅 Starting scheduler...")
        
        while True:
            now = datetime.now()
            
            if test_mode:
                # Test mode - run every minute
                next_run = now + timedelta(minutes=1)
                self.stdout.write(f"🧪 TEST MODE: Next backup in 1 minute")
            else:
                # Calculate next last day of month
                next_run = self.get_next_last_day(now, backup_time)
                sleep_seconds = (next_run - now).total_seconds()
                
                if sleep_seconds > 0:
                    days = int(sleep_seconds // (24 * 3600))
                    hours = int((sleep_seconds % (24 * 3600)) // 3600)
                    minutes = int((sleep_seconds % 3600) // 60)
                    
                    self.stdout.write(
                        f"💤 Next monthly backup in: {days} days, {hours} hours, {minutes} minutes"
                    )
                    self.stdout.write(f"📅 Scheduled for: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Sleep until next run
            if test_mode:
                time.sleep(60)  # 1 minute for testing
            else:
                time.sleep(max(1, sleep_seconds))
            
            # Perform backup
            self.perform_backup(log_file, test_mode)

    def get_next_last_day(self, from_date, backup_time):
        """Calculate the next last day of month after from_date"""
        year = from_date.year
        month = from_date.month
        
        # Parse backup time
        hour, minute = map(int, backup_time.split(':'))
        
        # Get last day of current month
        last_day = calendar.monthrange(year, month)[1]
        last_day_date = datetime(year, month, last_day, hour, minute, 0)
        
        # If we're past this month's last day, get next month's last day
        if from_date > last_day_date:
            # Move to next month
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
            
            last_day = calendar.monthrange(year, month)[1]
            last_day_date = datetime(year, month, last_day, hour, minute, 0)
        
        return last_day_date

    def is_last_day_of_month(self, date):
        """Check if given date is the last day of its month"""
        next_day = date + timedelta(days=1)
        return next_day.month != date.month

    def perform_backup(self, log_file, test_mode=False):
        """Perform the actual backup"""
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # Only run on last day of month (unless in test mode)
        if not test_mode and not self.is_last_day_of_month(now):
            self.stdout.write(f"⏭️ Skipping {timestamp} - Not last day of month")
            return
        
        month_name = now.strftime('%B %Y')
        
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(f"📅 [{timestamp}] Starting MONTHLY backup for {month_name}...")
        self.stdout.write(f"{'='*70}")
        
        # Log to file
        self.log_to_file(log_file, f"\n{'='*70}")
        self.log_to_file(log_file, f"[{timestamp}] Starting MONTHLY backup for {month_name}")
        
        try:
            # Database backup with month in filename
            self.stdout.write("  📀 Backing up database...")
            call_command('dbbackup', verbosity=0, interactive=False)
            self.stdout.write(self.style.SUCCESS("  ✅ Database backup completed"))
            self.log_to_file(log_file, "  ✅ Database backup completed")
            
            # Media backup with month in filename
            self.stdout.write("  🖼️ Backing up media files...")
            call_command('mediabackup', verbosity=0, interactive=False)
            self.stdout.write(self.style.SUCCESS("  ✅ Media backup completed"))
            self.log_to_file(log_file, "  ✅ Media backup completed")
            
            # Success message
            self.stdout.write(self.style.SUCCESS(
                f"\n✅ Monthly backup for {month_name} completed successfully!"
            ))
            self.log_to_file(log_file, f"✅ Monthly backup for {month_name} completed successfully")
            
            # Show backup location
            backup_dir = Path(__file__).resolve().parent.parent.parent.parent / 'backups'
            self.stdout.write(f"📁 Backups stored in: {backup_dir}")
            
        except Exception as e:
            error_msg = f"❌ Monthly backup failed: {str(e)}"
            self.stdout.write(self.style.ERROR(error_msg))
            self.log_to_file(log_file, error_msg)

    def log_to_file(self, log_file, message):
        """Write message to log file"""
        try:
            log_path = Path(__file__).resolve().parent.parent.parent.parent / log_file
            with open(log_path, 'a') as f:
                f.write(f"{message}\n")
        except:
            pass